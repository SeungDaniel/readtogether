import datetime
from typing import Optional

from google_sheets_client import GoogleSheetsClient


class LogRepository:
    """Append-only log sheet."""

    def __init__(self, sheets_client: GoogleSheetsClient, sheet_name: str) -> None:
        self.sheets_client = sheets_client
        self.sheet_name = sheet_name

    def append_log(
        self,
        chat_id: str,
        chat_type: str,
        username: str,
        command: str,
        status: str,
        note: Optional[str] = "",
    ) -> None:
        ts = datetime.datetime.utcnow().isoformat()
        range_ = f"{self.sheet_name}!A:F"
        self.sheets_client.append_row(
            range_,
            [ts, chat_id, chat_type, username or "", command, status, note or ""],
        )
