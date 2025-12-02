import datetime
import json
import logging
import time
import os
from typing import Optional, Dict, Any, Set

import requests

import config
from google_sheets_client import GoogleSheetsClient
from plan_repository import PlanRepository
from progress_repository import ProgressRepository
from group_repository import GroupRepository
from log_repository import LogRepository
import keyboard_factory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

POLL_TIMEOUT = int(os.environ.get("POLL_TIMEOUT_SECONDS", str(config.POLL_TIMEOUT)))

WELCOME_INLINE_KEYBOARD = None
if config.BOT_USERNAME:
    bot_link = f"https://t.me/{config.BOT_USERNAME}"
    WELCOME_INLINE_KEYBOARD = {
        "inline_keyboard": [
            [{"text": "개인 퀘스트 시작하기", "url": bot_link}],
        ]
    }


def today_date() -> datetime.date:
    if config.TIMEZONE:
        return datetime.datetime.now(tz=config.TIMEZONE).date()
    return datetime.date.today()


def send_message(
    chat_id: int,
    text: str,
    reply_markup: Optional[Dict[str, Any]] = None,
) -> None:
    url = f"{config.TELEGRAM_API_BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    response = requests.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)
    response.raise_for_status()


def answer_callback_query(callback_query_id: str, text: str = "") -> None:
    """Acknowledge a callback query to stop the loading animation."""
    url = f"{config.TELEGRAM_API_BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    requests.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)


def send_photo(
    chat_id: int,
    photo_url: str,
    caption: str,
    reply_markup: Optional[Dict[str, Any]] = None,
) -> None:
    url = f"{config.TELEGRAM_API_BASE_URL}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    response = requests.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)
    response.raise_for_status()


def set_message_reaction(chat_id: str, message_id: int, emoji: str = "👍") -> None:
    """React to a message with an emoji."""
    url = f"{config.TELEGRAM_API_BASE_URL}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}],
    }
    try:
        requests.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)
    except Exception:
        logging.warning("Failed to set reaction", exc_info=True)


def send_typing(chat_id: int) -> None:
    """Send 'typing' action to give user feedback during waits."""
    url = f"{config.TELEGRAM_API_BASE_URL}/sendChatAction"
    requests.post(
        url,
        json={"chat_id": chat_id, "action": "typing"},
        timeout=config.REQUEST_TIMEOUT,
    )


TOTAL_DAYS = 66

def build_plan_text(day: int, plan_row: dict, personal: bool = True) -> str:
    prefix = "개인" if personal else "공동체"
    ref = plan_row.get("ref", "")
    title = plan_row.get("title", "")
    summary = plan_row.get("summary", "")
    verse_text = plan_row.get("verse_text", "")
    
    progress_percent = int((day / TOTAL_DAYS) * 100)
    
    msg = f"[{prefix} DAY {day}] {ref} ({title})\n\n"
    
    if verse_text:
        msg += f"<i>\"{verse_text}\"</i>\n\n"
        
    msg += f"📖 이런 내용입니다:\n{summary}\n\n"
    msg += "인상 깊은 구절이나 한 줄 소감을 보내주셔도 좋습니다.\n"
    
    if personal:
        msg += "다음 퀘스트는 /next 로, 진행 현황은 /status 로 확인할 수 있어요."
    else:
        msg += f"진도율 : {day}/{TOTAL_DAYS} ({progress_percent}% 완료!)"
        
    return msg


class BotPolling:
    def __init__(self) -> None:
        self.offset: Optional[int] = None
        self.group_cache: Set[str] = set()
        
        # Fetch bot info dynamically
        self.bot_info = {}
        try:
            me_resp = requests.get(f"{config.TELEGRAM_API_BASE_URL}/getMe", timeout=10)
            me_resp.raise_for_status()
            self.bot_info = me_resp.json().get("result", {})
            logging.info("Bot info loaded: %s", self.bot_info)
        except Exception:
            logging.warning("Failed to fetch bot info (getMe)", exc_info=True)

        sheets_client = GoogleSheetsClient(
            spreadsheet_id=config.SPREADSHEET_ID,
            credentials_file=config.GOOGLE_SERVICE_ACCOUNT_FILE,
        )
        self.plan_repo = PlanRepository(sheets_client, config.PLAN_SHEET_NAME)
        self.progress_repo = ProgressRepository(sheets_client, config.PROGRESS_SHEET_NAME)
        self.group_repo = GroupRepository(sheets_client, config.GROUPS_SHEET_NAME)
        self.log_repo = LogRepository(sheets_client, config.LOG_SHEET_NAME)
        # preload existing groups to avoid duplicate welcome messages
        try:
            for g in self.group_repo.list_groups():
                self.group_cache.add(str(g["chat_id"]))
        except Exception:
            logging.debug("Failed to preload group cache", exc_info=True)

    def poll(self) -> None:
        while True:
            try:
                updates = self.get_updates()
                if updates:
                    self.handle_updates(updates)
            except Exception as exc:  # noqa: BLE001
                logging.error("Error in polling loop: %s", exc, exc_info=True)
                time.sleep(3)

    def get_updates(self) -> list:
        url = f"{config.TELEGRAM_API_BASE_URL}/getUpdates"
        params = {"timeout": POLL_TIMEOUT}
        if self.offset:
            params["offset"] = self.offset
        # Client timeout must be greater than server timeout (long polling)
        response = requests.get(url, params=params, timeout=POLL_TIMEOUT + 10)
        response.raise_for_status()
        data = response.json()
        return data.get("result", [])

    def handle_updates(self, updates: list) -> None:
        for upd in updates:
            self.offset = upd["update_id"] + 1
            
            # 1. Handle Callback Queries (Inline Buttons)
            if "callback_query" in upd:
                try:
                    self.handle_callback_query(upd["callback_query"])
                except Exception as exc:
                    logging.error("Error handling callback_query: %s", exc, exc_info=True)
                continue

            # 2. Handle My Chat Member (Bot added to group)
            if "my_chat_member" in upd:
                try:
                    self.handle_my_chat_member(upd["my_chat_member"])
                except Exception as exc:
                    logging.error("Error handling my_chat_member: %s", exc, exc_info=True)
                continue

            message = upd.get("message")
            if not message:
                continue
            
            chat = message.get("chat", {})
            chat_type = chat.get("type")
            chat_id = str(chat.get("id"))
            
            # 3. Handle Group Replies (Reaction)
            if chat_type in ("group", "supergroup"):
                reply_to = message.get("reply_to_message")
                if reply_to:
                    # Check if reply is to the bot
                    # We can check if 'from' in reply_to is the bot, but simpler is just to react if it's a reply
                    # Ideally we check if reply_to['from']['is_bot'] is True and username matches
                    # For now, let's just react to any reply to the bot's message
                    # But we need to know bot's ID or username. 
                    # Let's assume if it's a reply, we check if the original message was sent by us.
                    # Since we don't store our own ID easily without a getMe call, 
                    # we can rely on the fact that we only care if the user is replying to *us*.
                    # A safe heuristic: if reply_to_message exists and from.is_bot is True.
                    reply_from = reply_to.get("from", {})
                    
                    # Check if the message being replied to is from THIS bot
                    is_reply_to_me = False
                    my_username = self.bot_info.get("username")
                    my_id = self.bot_info.get("id")
                    
                    if my_id and reply_from.get("id") == my_id:
                        is_reply_to_me = True
                    elif my_username and reply_from.get("username") == my_username:
                        is_reply_to_me = True
                    elif not my_id and not my_username and reply_from.get("is_bot") and reply_from.get("username") == config.BOT_USERNAME:
                        # Fallback to config if getMe failed
                        is_reply_to_me = True
                        
                    if is_reply_to_me:
                         logging.info("Detected reply to bot in chat %s. Reacting...", chat_id)
                         set_message_reaction(chat_id, message["message_id"], "👍")
                         continue

            # 4. Handle Commands
            text = message.get("text") or ""
            if not text.startswith("/"):
                continue
            command = text.split()[0]
            
            try:
                if chat_type in ("group", "supergroup") and command == "/register_group":
                    self.handle_register_group(message)
                elif chat_type == "private":
                    if command == "/start":
                        self.handle_start_entry(message)
                    elif command == "/start_john":
                        self.handle_start(message)
                    elif command == "/next":
                        self.handle_next(message)
                    elif command == "/status":
                        self.handle_status(message)
                    elif command == "/repeat":
                        self.handle_repeat(message)
                    elif command == "/today_group":
                        self.handle_today_group(message)
                    elif command == "/reload":
                        self.plan_repo.reload()
                        send_message(int(chat_id), "Plan reloaded.")
            except Exception as exc:
                logging.error("Error handling update: %s", exc, exc_info=True)
                self.log_event(message, command, "error", str(exc))
            else:
                self.log_event(message, command, "ok")

    def handle_callback_query(self, cb: dict) -> None:
        cb_id = cb["id"]
        data = cb.get("data")
        message = cb.get("message")
        if not message or not data:
            answer_callback_query(cb_id)
            return

        chat_id = message["chat"]["id"]
        user_id = str(chat_id) # In private chat, chat_id is user_id
        
        # Debouncing could be added here if needed
        
        if data == "next":
            answer_callback_query(cb_id, "다음 퀘스트를 불러옵니다...")
            self.handle_next(message) # Reuse handle_next logic
        elif data == "repeat":
            answer_callback_query(cb_id, "다시 읽기")
            self.handle_repeat(message)
        elif data == "status":
            answer_callback_query(cb_id)
            self.handle_status(message)
        else:
            answer_callback_query(cb_id)

    def handle_start(self, message: dict) -> None:
        chat_id = message["chat"]["id"]
        username = message["from"].get("username", "")
        user_id = chat_id
        send_typing(chat_id)

        progress = self.progress_repo.get_progress(user_id)
        if progress:
            current_day = progress["current_day"]
            text = (
                "이미 요한복음 퀘스트를 진행 중입니다. 😊\n\n"
                f"- 현재 진행 단계: DAY {current_day}\n\n"
                "아래 버튼을 눌러 계속 진행해보세요."
            )
            send_message(chat_id, text, reply_markup=keyboard_factory.get_quest_keyboard())
            return

        self.progress_repo.upsert_progress(
            user_id=str(user_id), username=username, current_day=1, last_read_at=""
        )
        text = (
            "요한복음 데일리 퀘스트를 시작합니다. ✨\n"
            "지금부터 당신의 속도로, 1일차부터 차근차근 함께 읽을게요.\n\n"
            "준비가 되셨다면 아래 버튼을 눌러 첫 퀘스트를 받아보세요!"
        )
        send_message(chat_id, text, reply_markup=keyboard_factory.get_start_keyboard())

    def handle_start_entry(self, message: dict) -> None:
        chat_id = message["chat"]["id"]
        send_typing(chat_id)
        text = (
            "안녕하세요! 요한복음 봇입니다. 🙌\n\n"
            "개인 퀘스트를 시작하려면 아래 버튼을 눌러주세요."
        )
        # Reuse start keyboard or make a specific one
        kb = {
            "inline_keyboard": [[{"text": "개인 퀘스트 시작 (/start_john)", "callback_data": "start_john_cmd"}]] 
        }
        # Note: I didn't add start_john_cmd to handle_callback_query yet, let's just guide them to type it or use a deep link
        # Actually, let's just tell them to type /start_john for now or use the button if I implement it.
        # Simpler: Just guide them.
        text = (
            "안녕하세요! 요한복음 봇입니다. 🙌\n\n"
            "개인 퀘스트를 시작하려면 /start_john 을 입력해주세요."
        )
        send_message(chat_id, text)

    def handle_next(self, message: dict) -> None:
        chat_id = message["chat"]["id"]
        username = message["from"].get("username", "")
        user_id = chat_id
        send_typing(chat_id)

        progress = self.progress_repo.get_progress(user_id)
        if not progress:
            send_message(chat_id, "먼저 /start_john 으로 퀘스트를 시작해주세요.")
            return

        day = progress["current_day"]
        plan_row = self.plan_repo.get_plan_by_day(day)
        if not plan_row:
            send_message(
                chat_id,
                "더 이상 준비된 퀘스트가 없습니다. 축하합니다, 완주하셨습니다! 🎉",
            )
            return

        text = build_plan_text(day, plan_row, personal=True)
        image_url = plan_row.get("image_url", "").strip()
        
        if image_url:
            send_photo(chat_id, image_url, text, reply_markup=keyboard_factory.get_quest_keyboard())
        else:
            send_message(chat_id, text, reply_markup=keyboard_factory.get_quest_keyboard())

        today_str = today_date().isoformat()
        self.progress_repo.upsert_progress(
            user_id=str(user_id),
            username=username,
            current_day=day + 1,
            last_read_at=today_str,
        )

    def handle_status(self, message: dict) -> None:
        chat_id = message["chat"]["id"]
        user_id = chat_id
        send_typing(chat_id)

        progress = self.progress_repo.get_progress(user_id)
        if not progress:
            send_message(
                chat_id,
                "아직 요한복음 퀘스트를 시작하지 않으셨습니다. /start_john 으로 시작할 수 있어요.",
            )
            return

        next_day = progress["current_day"]
        finished_day = max(0, next_day - 1)
        plan_row = self.plan_repo.get_plan_by_day(next_day)
        if plan_row:
            ref = plan_row.get("ref", "")
            title = plan_row.get("title", "")
            text = (
                "🔎 나의 요한복음 퀘스트 현황\n\n"
                f"- 완료한 퀘스트: DAY {finished_day}\n"
                f"- 다음 퀘스트: DAY {next_day} – {ref} ({title})"
            )
        else:
            text = (
                "🔎 나의 요한복음 퀘스트 현황\n\n"
                f"- 완료한 퀘스트: DAY {finished_day}\n"
                "이미 준비된 모든 퀘스트를 완료하셨습니다. 🎉"
            )
        send_message(chat_id, text, reply_markup=keyboard_factory.get_quest_keyboard())

    def handle_repeat(self, message: dict) -> None:
        chat_id = message["chat"]["id"]
        user_id = chat_id
        send_typing(chat_id)

        progress = self.progress_repo.get_progress(user_id)
        if not progress:
            send_message(
                chat_id,
                "아직 요한복음 퀘스트를 시작하지 않으셨습니다. /start_john 으로 시작할 수 있어요.",
            )
            return

        repeat_day = progress["current_day"] - 1
        if repeat_day <= 0:
            send_message(
                chat_id, "아직 완료한 퀘스트가 없습니다. /next 로 첫 퀘스트를 받아보세요.", reply_markup=keyboard_factory.get_start_keyboard()
            )
            return

        plan_row = self.plan_repo.get_plan_by_day(repeat_day)
        if not plan_row:
            send_message(chat_id, "직전 퀘스트 정보를 찾을 수 없습니다.")
            return

        text = build_plan_text(repeat_day, plan_row, personal=True)
        # Override text for repeat context if needed, but build_plan_text is generic now.
        # Let's just prepend the "Last read" context or rely on build_plan_text's header.
        # build_plan_text uses "[개인 DAY N]" header.
        # Let's stick to the standard format for consistency, or modify build_plan_text to accept a prefix override?
        # For simplicity, let's use the standard text which is rich enough.
        
        image_url = plan_row.get("image_url", "").strip()
        if image_url:
             send_photo(chat_id, image_url, text, reply_markup=keyboard_factory.get_quest_keyboard())
        else:
             send_message(chat_id, text, reply_markup=keyboard_factory.get_quest_keyboard())

    # handle_previous removed as it is not in the new spec and inline buttons handle navigation better.


    def handle_today_group(self, message: dict) -> None:
        """Allow personal DM to see today's 공동체 본문 (first group config)."""
        chat_id = message["chat"]["id"]
        send_typing(chat_id)
        if not config.GROUPS:
            send_message(chat_id, "그룹 설정이 없습니다.", use_default_keyboard=True)
            return
        group = config.GROUPS[0]
        tz = group.get("timezone") or config.TIMEZONE
        start_date = group["start_date"]
        plan_sheet = group["plan_sheet"]

        now_local = datetime.datetime.now(tz=tz) if tz else datetime.datetime.now()
        day = (now_local.date() - start_date).days + 1
        if day <= 0:
            send_message(chat_id, "공동체 DAY가 아직 시작 전입니다.")
            return

        plan_row = self.plan_repo.get_plan_by_day(day)
        if not plan_row:
            send_message(chat_id, f"공동체 DAY {day} 정보를 찾지 못했습니다.")
            return

        text = build_plan_text(day, plan_row, personal=False)
        send_message(chat_id, text)

    def handle_register_group(self, message: dict) -> None:
        chat = message.get("chat", {})
        chat_type = chat.get("type", "")
        chat_id = str(chat.get("id"))
        if chat_type not in ("group", "supergroup"):
            send_message(chat.get("id"), "이 명령은 그룹/슈퍼그룹에서만 사용할 수 있습니다.")
            return
        title = chat.get("title", "")
        plan_sheet = config.PLAN_SHEET_NAME
        start_date = config.START_DATE
        tz = os.environ.get("TIMEZONE", "Asia/Seoul")
        try:
            self.group_repo.append_group(chat_id, plan_sheet, start_date, tz)
            self.group_cache.add(chat_id)
            send_message(
                chat.get("id"),
                f"그룹이 등록되었습니다.\nchat_id={chat_id}\nplan_sheet={plan_sheet}\nstart_date={start_date}\ntimezone={tz}",
            )
            self.log_event(message, "/register_group", "ok", f"title={title}")
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed to register group: %s", exc, exc_info=True)
            send_message(chat.get("id"), "그룹 등록 중 오류가 발생했습니다. 나중에 다시 시도해주세요.")
            self.log_event(message, "/register_group", "error", str(exc))

    def handle_my_chat_member(self, member_update: dict) -> None:
        chat = member_update.get("chat", {})
        chat_type = chat.get("type")
        if chat_type not in ("group", "supergroup"):
            return
        new_status = member_update.get("new_chat_member", {}).get("status")
        if new_status not in ("member", "administrator"):
            return
        chat_id = str(chat.get("id"))
        if chat_id in self.group_cache:
            return
        plan_sheet = config.PLAN_SHEET_NAME
        start_date = config.START_DATE
        tz = os.environ.get("TIMEZONE", "Asia/Seoul")
        try:
            self.group_repo.append_group(chat_id, plan_sheet, start_date, tz)
            self.group_cache.add(chat_id)
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed to auto-register group: %s", exc, exc_info=True)
        welcome_text = (
            "안녕하세요! 요한복음 공동체 봇입니다. 🙌\n"
            "이 방은 기본 설정으로 등록되었습니다. 시작일/플랜/타임존이 필요에 맞는지 시트에서 확인해주세요.\n"
            "개인 퀘스트는 DM에서 /start_john 으로 시작할 수 있어요."
        )
        send_message(chat.get("id"), welcome_text, reply_markup=WELCOME_INLINE_KEYBOARD)
        self.log_event_simple(chat_id, chat_type, "", "my_chat_member", "ok", "auto-registered")

    def log_event(self, message: dict, command: str, status: str, note: str = "") -> None:
        try:
            chat = message.get("chat", {})
            chat_id = str(chat.get("id"))
            chat_type = chat.get("type", "")
            username = ""
            frm = message.get("from")
            if frm:
                username = frm.get("username", "") or frm.get("first_name", "")
            self.log_repo.append_log(chat_id, chat_type, username, command, status, note)
        except Exception:
            logging.debug("log_event failed", exc_info=True)

    def log_event_simple(
        self, chat_id: str, chat_type: str, username: str, command: str, status: str, note: str = ""
    ) -> None:
        try:
            self.log_repo.append_log(chat_id, chat_type, username, command, status, note)
        except Exception:
            logging.debug("log_event_simple failed", exc_info=True)


def main() -> None:
    bot = BotPolling()
    bot.poll()


if __name__ == "__main__":
    main()
