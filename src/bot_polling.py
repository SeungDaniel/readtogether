import datetime
import json
import logging
import time
import os
from typing import Optional, Dict, Any, Set

import requests

import config
import constants
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
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
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
    # Telegram caption limit is 1024 characters.
    # If caption is too long, split into Photo + Text Message.
    if len(caption) > 1000:
        try:
            # 1. Send Photo (empty caption)
            url = f"{config.TELEGRAM_API_BASE_URL}/sendPhoto"
            payload = {"chat_id": chat_id, "photo": photo_url}
            requests.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)
            
            # 2. Send Text (with markup)
            send_message(chat_id, caption, reply_markup)
            return
        except Exception:
            logging.warning("Failed to send split photo, falling back to text only", exc_info=True)
            send_message(chat_id, caption, reply_markup)
            return

    # Normal attempt for short captions
    url = f"{config.TELEGRAM_API_BASE_URL}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
        
    try:
        response = requests.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            logging.warning("sendPhoto failed with 400 (Bad Request), falling back to text only. URL: %s", photo_url)
            send_message(chat_id, caption, reply_markup)
        else:
            raise


def set_message_reaction(chat_id: str, message_id: int, emoji: str = constants.EMOJI_REACTION) -> None:
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
    
    mt = plan_row.get("mt", "").strip()
    mk = plan_row.get("mk", "").strip()
    lk = plan_row.get("lk", "").strip()
    
    # Helper to check if a parallel ref is valid (has content and not "독자 기록" or "-")
    def is_valid_parallel(text: str) -> bool:
        return bool(text) and text not in ("-", "독자 기록")
    
    has_parallel = is_valid_parallel(mt) or is_valid_parallel(mk) or is_valid_parallel(lk)
    
    progress_percent = int((day / TOTAL_DAYS) * 100)
    
    msg = f"[{prefix} DAY {day}] {ref} ({title})\n\n"
    
    if verse_text:
        msg += f"<blockquote>{verse_text}</blockquote>\n\n"
        
    if has_parallel:
        msg += "📖 평행본문 (Parallel Gospels)\n"
        if is_valid_parallel(mt):
            msg += f"• 마태(Mt): {mt}\n"
        if is_valid_parallel(mk):
            msg += f"• 마가(Mk): {mk}\n"
        if is_valid_parallel(lk):
            msg += f"• 누가(Lk): {lk}\n"
        msg += "\n"
        # Optional: Still show summary if parallel exists? User said "Instead of summary".
        # Let's assume we replace summary with parallel if parallel exists.
        # But if user wants summary + parallel, we can add it back.
        # User said: "오늘의 말씀과, 요약 대신에 평행본문 소개하는걸로" -> So replace summary.
    else:
        # No parallel (Unique to John)
        # User said: "요한복음에만 기록됐으면 오늘의 말씀(요약x)" -> So NO summary here either.
        # Wait, if unique, show ONLY verse text.
        pass
        
    # User instruction: "요한복음에만 기록됐으면 오늘의 말씀(요약x), 평행본문이 존재하면 평행본문 소개."
    # This implies Summary is GONE in both cases for Personal Mode.
    # But let's keep Summary for Community Mode (personal=False) if needed?
    # The request said "개인모드에서 먼저...".
    # Let's apply this logic for personal=True.
    
    if not personal:
        # For community mode, keep original behavior (Summary)
        msg += f"{constants.EMOJI_BOOK} 이런 내용입니다:\n{summary}\n\n"
    
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
            
            # 3. Handle Group Replies (Reaction) & Auto-Linking
            if chat_type in ("group", "supergroup"):
                # Auto-Link User to Group
                user = message.get("from")
                if user and not user.get("is_bot"):
                    user_id = str(user.get("id"))
                    username = user.get("username", "")
                    self.link_user_to_group(user_id, username, chat_id)

                reply_to = message.get("reply_to_message")
                if reply_to:
                    # Check if reply is to the bot
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
                         set_message_reaction(chat_id, message["message_id"], constants.EMOJI_REACTION)
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

    def link_user_to_group(self, user_id: str, username: str, group_id: str) -> None:
        """Add group_id to user's progress if not already present."""
        try:
            progress = self.progress_repo.get_progress(user_id)
            current_day = 1
            group_ids = []
            
            if progress:
                current_day = progress["current_day"]
                group_ids = progress.get("group_ids", [])
            
            if group_id not in group_ids:
                group_ids.append(group_id)
                logging.info("Linking user %s to group %s", user_id, group_id)
                self.progress_repo.upsert_progress(
                    user_id=user_id,
                    username=username,
                    current_day=current_day,
                    group_ids=group_ids
                )
        except Exception:
            logging.error("Failed to link user to group", exc_info=True)

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
            text = constants.MSG_ALREADY_STARTED.format(current_day=current_day)
            send_message(chat_id, text, reply_markup=keyboard_factory.get_quest_keyboard())
            return

        self.progress_repo.upsert_progress(
            user_id=str(user_id), username=username, current_day=1, last_read_at=""
        )
        text = constants.MSG_QUEST_START
        send_message(chat_id, text, reply_markup=keyboard_factory.get_start_keyboard())

    def handle_start_entry(self, message: dict) -> None:
        chat_id = message["chat"]["id"]
        send_typing(chat_id)
        text = constants.MSG_WELCOME
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
                constants.MSG_NO_QUEST,
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
                constants.MSG_NOT_STARTED,
            )
            return

        next_day = progress["current_day"]
        finished_day = max(0, next_day - 1)
        plan_row = self.plan_repo.get_plan_by_day(next_day)
        if plan_row:
            ref = plan_row.get("ref", "")
            title = plan_row.get("title", "")
            text = constants.MSG_STATUS_HEADER + constants.MSG_STATUS_BODY.format(finished_day=finished_day, next_day=next_day, ref=ref, title=title)
        else:
            text = constants.MSG_STATUS_HEADER + constants.MSG_STATUS_FINISHED.format(finished_day=finished_day)
        send_message(chat_id, text, reply_markup=keyboard_factory.get_quest_keyboard())

    def handle_repeat(self, message: dict) -> None:
        chat_id = message["chat"]["id"]
        user_id = chat_id
        send_typing(chat_id)

        progress = self.progress_repo.get_progress(user_id)
        if not progress:
            send_message(
                chat_id,
                constants.MSG_NOT_STARTED,
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
        
        image_url = plan_row.get("image_url", "").strip()
        if image_url:
             send_photo(chat_id, image_url, text, reply_markup=keyboard_factory.get_quest_keyboard())
        else:
             send_message(chat_id, text, reply_markup=keyboard_factory.get_quest_keyboard())

    def handle_today_group(self, message: dict) -> None:
        """Show today's plan for the user's linked groups."""
        chat_id = message["chat"]["id"]
        user_id = str(chat_id)
        send_typing(chat_id)
        
        # 1. Get User's Linked Groups
        progress = self.progress_repo.get_progress(user_id)
        linked_group_ids = progress.get("group_ids", []) if progress else []
        
        # 2. Fetch All Groups Config
        all_groups = self.group_repo.list_groups()
        
        # 3. Filter Linked Groups
        target_groups = []
        if linked_group_ids:
            target_groups = [g for g in all_groups if str(g["chat_id"]) in linked_group_ids]
        
        # Fallback: If no linked groups, try to show the first available group (or error)
        if not target_groups:
            if all_groups:
                # Optional: Show first group as default, or tell user to join a group
                # For now, let's show the first one but maybe add a note?
                # Or strictly require membership. Let's be friendly and show first one.
                target_groups = [all_groups[0]]
            else:
                send_message(chat_id, "등록된 그룹이 없습니다.", use_default_keyboard=True)
                return

        # 4. Send Plan for Each Target Group
        for group in target_groups:
            tz = group.get("timezone") or config.TIMEZONE
            start_date = group["start_date"]
            # group_title = group.get("title", "공동체") # If we had title in repo
            
            try:
                from zoneinfo import ZoneInfo
                tz_info = ZoneInfo(tz) if tz else None
            except Exception:
                logging.warning("Invalid timezone %s, falling back to local", tz)
                tz_info = None

            now_local = datetime.datetime.now(tz=tz_info)
            day = (now_local.date() - start_date).days + 1
            
            if day <= 0:
                send_message(chat_id, f"공동체(ID:{group['chat_id']}) DAY가 아직 시작 전입니다.")
                continue

            plan_row = self.plan_repo.get_plan_by_day(day)
            if not plan_row:
                send_message(chat_id, f"공동체(ID:{group['chat_id']}) DAY {day} 정보를 찾지 못했습니다.")
                continue

            text = build_plan_text(day, plan_row, personal=True)
            # Add a header to distinguish groups if multiple
            if len(target_groups) > 1:
                text = f"📢 <b>그룹 {group['chat_id']}</b>\n\n" + text
                
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
