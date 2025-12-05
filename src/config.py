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


TELEGRAM_BOT_TOKEN: str = _get_env_or_raise("TELEGRAM_BOT_TOKEN")

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
            print(f"!! Critical Error: Service Account Key file not found.")
            print(f"   - Env var value: '{os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE')}'")
            print(f"   - Searched in: {_config_dir}")

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

# Note: Group configuration is now handled exclusively via Google Sheets (GroupRepository).
# TELEGRAM_GROUP_CHAT_IDS and TELEGRAM_GROUP_CONFIG are deprecated.
