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
from group_repository import GroupRepository

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


TOTAL_DAYS = 66  # Based on the screenshot (n/66)


def build_message(plan_row: dict, day: int) -> str:
    ref = html.escape(plan_row.get("ref", ""))
    title = html.escape(plan_row.get("title", ""))
    summary = html.escape(plan_row.get("summary", ""))
    verse_text = html.escape(plan_row.get("verse_text", ""))
    verse_ref = html.escape(plan_row.get("verse_ref", ""))
    
    # Calculate progress
    progress_percent = int((day / TOTAL_DAYS) * 100)
    
    msg = f"[요한복음 함께 읽기 DAY {day}]\n\n"
    msg += "오늘의 범위는\n"
    msg += f"🌈 <b>{ref} ({title})</b>입니다.\n\n"


    if verse_text:
        msg += f"📖<b>오늘의 말씀</b>\n<i>\"{verse_text}\" ({verse_ref})</i>\n\n"
    
    msg += "읽고 퀴즈를 내거나, 인상깊은 구절을 공유하는 등 자유롭게 인증해주세요. 🙌\n\n"
    
    msg += f"진도율 : {day}/{TOTAL_DAYS} ({progress_percent}% 완료!)\n\n"
    
    msg += "📚<b>참고자료</b>\n"
    msg += '- <a href="https://t.me/c/1829333998/244/361?single">[지도] 예수님 당시의 이스라엘</a>\n'
    msg += '- <a href="http://www.biblemap.or.kr/biblemapMobile.html">성경 지도(추천)</a>'
    
    return msg


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


def send_photo(chat_id: str, photo_url: str, caption: str, message_thread_id: Optional[int] = None) -> None:
    url = f"{config.TELEGRAM_API_BASE_URL}/sendPhoto"
    
    # Handle local file paths
    if photo_url.startswith("file://"):
        photo_path = photo_url[7:]  # Strip 'file://'
    elif photo_url.startswith("/"):
        photo_path = photo_url
    else:
        photo_path = None

    if photo_path and os.path.exists(photo_path):
        # Send local file
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"}
            if message_thread_id is not None:
                data["message_thread_id"] = str(message_thread_id)
            
            response = requests.post(url, data=data, files=files, timeout=config.REQUEST_TIMEOUT + 10)
            response.raise_for_status()
    else:
        # Send URL
        payload = {
            "chat_id": chat_id, 
            "photo": photo_url, 
            "caption": caption, 
            "parse_mode": "HTML"
        }
        if message_thread_id is not None:
            payload["message_thread_id"] = message_thread_id
        response = requests.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()


def main() -> None:
    sheets_client = GoogleSheetsClient(
        spreadsheet_id=config.SPREADSHEET_ID,
        credentials_file=config.GOOGLE_SERVICE_ACCOUNT_FILE,
    )
    groups = config.GROUPS
    if config.GROUPS_FROM_SHEET:
        group_repo = GroupRepository(sheets_client, config.GROUPS_SHEET_NAME)
        sheet_groups = group_repo.list_groups()
        if sheet_groups:
            groups = [
                {
                    "chat_id": g["chat_id"],
                    "plan_sheet": g.get("plan_sheet") or config.PLAN_SHEET_NAME,
                    "start_date": g.get("start_date") or config.START_DATE,
                    "timezone": (
                        config.ZoneInfo(g["timezone"])
                        if g.get("timezone") and config.ZoneInfo
                        else config.TIMEZONE
                    ),
                }
                for g in sheet_groups
            ]
    if not groups:
        logging.error("No group configuration found.")
        return

    today = _now()
    plan_repos = {}

    for group in groups:
        chat_id_raw = group["chat_id"]
        chat_id, thread_id = parse_chat_destination(chat_id_raw)
        start_date = group.get("start_date") or config.START_DATE
        plan_sheet = group.get("plan_sheet") or config.PLAN_SHEET_NAME
        tz = group.get("timezone") or config.TIMEZONE

        now_local = datetime.datetime.now(tz=tz) if tz else today
        day = calculate_day(now_local, start_date)
        if day is None:
            logging.info(
                "Start date is in the future for chat_id=%s; skipping.", chat_id
            )
            continue

        if plan_sheet not in plan_repos:
            plan_repos[plan_sheet] = PlanRepository(sheets_client, plan_sheet)
        plan_repo = plan_repos[plan_sheet]
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
        image_url = plan_row.get("image_url", "").strip()

        if DRY_RUN:
            logging.info(
                "[DRY_RUN] Would send to chat_id=%s (sheet=%s, start=%s):\n%s\n[Image]: %s",
                chat_id_raw,
                plan_sheet,
                start_date,
                message,
                image_url,
            )
            continue

        try:
            if image_url:
                send_photo(chat_id, image_url, message, thread_id)
                logging.info(
                    "Sent day %s photo+message to chat_id=%s (sheet=%s)", day, chat_id_raw, plan_sheet
                )
            else:
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
