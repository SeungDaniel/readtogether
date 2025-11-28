import datetime
import logging
import os
import re
import html
from typing import Optional, Tuple

import requests

import config
from google_sheets_client import GoogleSheetsClient
from plan_repository import PlanRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

DRY_RUN = os.environ.get("DRY_RUN", "").lower() == "true"


def _now() -> datetime.datetime:
    if config.TIMEZONE:
        return datetime.datetime.now(tz=config.TIMEZONE)
    return datetime.datetime.now()


def calculate_day(today: datetime.datetime, start_date: datetime.date) -> Optional[int]:
    day_index = (today.date() - start_date).days
    if day_index < 0:
        return None
    return day_index + 1


def build_message(plan_row: dict, day: int) -> str:
    ref = html.escape(plan_row.get("ref", ""))
    title = html.escape(plan_row.get("title", ""))
    summary = html.escape(plan_row.get("summary", ""))
    return (
        f"[요한복음 함께 읽기 DAY {day}]\n\n"
        "오늘의 범위는\n"
        f"🌈 {ref} ({title})입니다.\n\n"
        "📖 무슨 내용인가요?\n"
        f"{summary}\n\n"
        "읽고 퀴즈를 내거나, 인상깊은 구절을 공유하는 등 자유롭게 인증해주세요. 🙌\n\n"
        "📚참고자료\n"
        '- <a href="https://t.me/c/1829333998/244/361?single">[지도] 예수님 당시의 이스라엘</a>\n'
        '- <a href="http://www.biblemap.or.kr/biblemapMobile.html">성경 지도(추천)</a>'
    )


def parse_chat_destination(chat_id_str: str) -> Tuple[str, Optional[int]]:
    """Allow chat ids like '-100123_456' where 456 is a topic/thread id."""
    match = re.match(r"(?P<chat>-?\d+)(?:_(?P<thread>\d+))?$", chat_id_str.strip())
    if match:
        chat = match.group("chat")
        thread = match.group("thread")
        return chat, int(thread) if thread else None
    return chat_id_str, None


def send_message(chat_id: str, text: str, message_thread_id: Optional[int] = None) -> None:
    url = f"{config.TELEGRAM_API_BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if message_thread_id is not None:
        payload["message_thread_id"] = message_thread_id
    response = requests.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)
    response.raise_for_status()


def main() -> None:
    if not config.GROUPS:
        logging.error("No group configuration found.")
        return

    today = _now()
    sheets_client = GoogleSheetsClient(
        spreadsheet_id=config.SPREADSHEET_ID,
        credentials_file=config.GOOGLE_SERVICE_ACCOUNT_FILE,
    )
    for group in config.GROUPS:
        chat_id_raw = group["chat_id"]
        chat_id, thread_id = parse_chat_destination(chat_id_raw)
        start_date = group["start_date"]
        plan_sheet = group["plan_sheet"]

        day = calculate_day(today, start_date)
        if day is None:
            logging.info(
                "Start date is in the future for chat_id=%s; skipping.", chat_id
            )
            continue

        plan_repo = PlanRepository(sheets_client, plan_sheet)
        plan_row = plan_repo.get_plan_by_day(day)
        if not plan_row:
            logging.warning(
                "No plan found for day=%s in sheet=%s; chat_id=%s; nothing sent.",
                day,
                plan_sheet,
                chat_id,
            )
            continue

        message = build_message(plan_row, day)
        if DRY_RUN:
            logging.info(
                "[DRY_RUN] Would send to chat_id=%s (sheet=%s, start=%s):\n%s",
                chat_id_raw,
                plan_sheet,
                start_date,
                message,
            )
            continue

        try:
            send_message(chat_id, message, thread_id)
            logging.info(
                "Sent day %s message to chat_id=%s (sheet=%s)", day, chat_id_raw, plan_sheet
            )
        except requests.RequestException as exc:
            logging.error(
                "Failed to send message to chat_id=%s: %s", chat_id, exc, exc_info=True
            )


if __name__ == "__main__":
    main()
