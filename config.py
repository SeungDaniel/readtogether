import os
import json
import datetime
from typing import List, Dict, Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python <3.9 fallback
    ZoneInfo = None  # type: ignore


def _get_env_or_raise(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _parse_group_ids() -> List[str]:
    ids_env = os.environ.get("TELEGRAM_GROUP_CHAT_IDS")
    if ids_env:
        # Comma-separated list of chat ids
        ids = [item.strip() for item in ids_env.split(",") if item.strip()]
        if ids:
            return ids
    single_id = os.environ.get("TELEGRAM_GROUP_CHAT_ID")
    return [single_id] if single_id else []


TELEGRAM_BOT_TOKEN: str = _get_env_or_raise("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_CHAT_IDS: List[str] = _parse_group_ids()

GOOGLE_SERVICE_ACCOUNT_FILE: str = _get_env_or_raise("GOOGLE_SERVICE_ACCOUNT_FILE")
SPREADSHEET_ID: str = _get_env_or_raise("SPREADSHEET_ID")

PLAN_SHEET_NAME: str = os.environ.get("PLAN_SHEET_NAME", "plan")
PROGRESS_SHEET_NAME: str = os.environ.get("PROGRESS_SHEET_NAME", "progress")

START_DATE_STR: str = os.environ.get("START_DATE", "2025-12-01")
START_DATE: datetime.date = datetime.datetime.strptime(
    START_DATE_STR, "%Y-%m-%d"
).date()

TIMEZONE_NAME: str = os.environ.get("TIMEZONE", "Asia/Seoul")
TIMEZONE = ZoneInfo(TIMEZONE_NAME) if ZoneInfo else None

TELEGRAM_API_BASE_URL: str = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

REQUEST_TIMEOUT: int = int(os.environ.get("REQUEST_TIMEOUT_SECONDS", "15"))


def _parse_date(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def _parse_group_config() -> List[Dict[str, Any]]:
    """Allow per-group plan sheet and start_date overrides.

    TELEGRAM_GROUP_CONFIG expects a JSON array of:
      [{"chat_id": "...", "plan_sheet": "plan_a", "start_date": "2025-12-01"}, ...]
    """
    raw = os.environ.get("TELEGRAM_GROUP_CONFIG")
    groups: List[Dict[str, Any]] = []
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                for item in data:
                    chat_id = str(item.get("chat_id", "")).strip()
                    if not chat_id:
                        continue
                    plan_sheet = item.get("plan_sheet", PLAN_SHEET_NAME)
                    start_date_str = item.get("start_date", START_DATE_STR)
                    try:
                        start_date = _parse_date(start_date_str)
                    except ValueError:
                        start_date = START_DATE
                    groups.append(
                        {
                            "chat_id": chat_id,
                            "plan_sheet": plan_sheet,
                            "start_date": start_date,
                        }
                    )
        except json.JSONDecodeError:
            raise RuntimeError(
                "Failed to parse TELEGRAM_GROUP_CONFIG; must be valid JSON array."
            )

    if not groups and TELEGRAM_GROUP_CHAT_IDS:
        groups = [
            {"chat_id": cid, "plan_sheet": PLAN_SHEET_NAME, "start_date": START_DATE}
            for cid in TELEGRAM_GROUP_CHAT_IDS
        ]
    return groups


GROUPS = _parse_group_config()
