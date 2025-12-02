import os
import json
import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load .env explicitly from config/ folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, "config", ".env")
load_dotenv(ENV_PATH)

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
        # Comma-separated list of chat ids, ignoring comments
        ids = [
            item.strip() 
            for item in ids_env.split(",") 
            if item.strip() and not item.strip().startswith("#")
        ]
        if ids:
            return ids
    single_id = os.environ.get("TELEGRAM_GROUP_CHAT_ID")
    if single_id and not single_id.strip().startswith("#"):
        return [single_id.strip()]
    return []


TELEGRAM_BOT_TOKEN: str = _get_env_or_raise("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_CHAT_IDS: List[str] = _parse_group_ids()

GOOGLE_SERVICE_ACCOUNT_FILE: str = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "")

# 1. Check if file exists as-is
if not os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
    # 2. Check in config/ directory using BASE_DIR
    _config_dir = os.path.join(BASE_DIR, "config")
    _candidate = os.path.join(_config_dir, GOOGLE_SERVICE_ACCOUNT_FILE)
    
    if os.path.exists(_candidate):
        GOOGLE_SERVICE_ACCOUNT_FILE = _candidate
    else:
        # 3. Fallback: Find any json file in config/ that looks like a key
        _found = False
        if os.path.exists(_config_dir):
            for _f in os.listdir(_config_dir):
                if _f.endswith(".json") and "readtogether" in _f:
                    GOOGLE_SERVICE_ACCOUNT_FILE = os.path.join(_config_dir, _f)
                    _found = True
                    break
        
        if not _found:
            # Print debug info to help user
            print(f"!! Critical Error: Service Account Key file not found.")
            print(f"   - Env var value: '{os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE')}'")
            print(f"   - Searched in: {_config_dir}")
            # Let it fail later or raise here, but _get_env_or_raise might have been better. 
            # We will let the next line fail if it's empty.

if not GOOGLE_SERVICE_ACCOUNT_FILE:
     raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_FILE not set or file not found.")

SPREADSHEET_ID: str = _get_env_or_raise("SPREADSHEET_ID")

PLAN_SHEET_NAME: str = os.environ.get("PLAN_SHEET_NAME", "plan")
PROGRESS_SHEET_NAME: str = os.environ.get("PROGRESS_SHEET_NAME", "progress")
GROUPS_SHEET_NAME: str = os.environ.get("GROUPS_SHEET_NAME", "groups")
GROUPS_FROM_SHEET: bool = os.environ.get("GROUPS_FROM_SHEET", "false").lower() == "true"
LOG_SHEET_NAME: str = os.environ.get("LOG_SHEET_NAME", "logs")

START_DATE_STR: str = os.environ.get("START_DATE", "2025-12-01")
START_DATE: datetime.date = datetime.datetime.strptime(
    START_DATE_STR, "%Y-%m-%d"
).date()

TIMEZONE_NAME: str = os.environ.get("TIMEZONE", "Asia/Seoul")
TIMEZONE = ZoneInfo(TIMEZONE_NAME) if ZoneInfo else None

TELEGRAM_API_BASE_URL: str = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

REQUEST_TIMEOUT: int = int(os.environ.get("REQUEST_TIMEOUT_SECONDS", "15"))
POLL_TIMEOUT: int = int(os.environ.get("POLL_TIMEOUT_SECONDS", "20"))
BOT_USERNAME: str = os.environ.get("BOT_USERNAME", "")


def _parse_date(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def _parse_group_config() -> List[Dict[str, Any]]:
    """Allow per-group plan sheet and start_date overrides.

    TELEGRAM_GROUP_CONFIG expects a JSON array of:
      [{"chat_id": "...", "plan_sheet": "plan_a", "start_date": "2025-12-01", "timezone": "Asia/Seoul"}, ...]
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
                    tz_name: Optional[str] = item.get("timezone")
                    tz = ZoneInfo(tz_name) if tz_name and ZoneInfo else TIMEZONE
                    try:
                        start_date = _parse_date(start_date_str)
                    except ValueError:
                        start_date = START_DATE
                    groups.append(
                        {
                            "chat_id": chat_id,
                            "plan_sheet": plan_sheet,
                            "start_date": start_date,
                            "timezone": tz,
                        }
                    )
        except json.JSONDecodeError:
            raise RuntimeError(
                "Failed to parse TELEGRAM_GROUP_CONFIG; must be valid JSON array."
            )

    if not groups and TELEGRAM_GROUP_CHAT_IDS:
        groups = [
            {
                "chat_id": cid,
                "plan_sheet": PLAN_SHEET_NAME,
                "start_date": START_DATE,
                "timezone": TIMEZONE,
            }
            for cid in TELEGRAM_GROUP_CHAT_IDS
        ]
    return groups


GROUPS = _parse_group_config()
