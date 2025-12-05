import datetime
from typing import Optional, Dict, Any, List

from google_sheets_client import GoogleSheetsClient


class ProgressRepository:
    """Simple sheet-backed progress store."""

    def __init__(self, sheets_client: GoogleSheetsClient, sheet_name: str) -> None:
        self.sheets_client = sheets_client
        self.sheet_name = sheet_name

    def _rows(self) -> List[List[Any]]:
        range_ = f"{self.sheet_name}!A2:E"
        return self.sheets_client.get_values(range_)

    def get_progress(self, user_id: str) -> Optional[Dict[str, Any]]:
        rows = self._rows()
        for idx, row in enumerate(rows, start=2):
            if not row:
                continue
            if str(row[0]).strip() == str(user_id):
                group_ids_str = row[4] if len(row) > 4 else ""
                group_ids = [g.strip() for g in group_ids_str.split(",") if g.strip()]
                return {
                    "row_index": idx,
                    "user_id": row[0],
                    "username": row[1] if len(row) > 1 else "",
                    "current_day": int(row[2]) if len(row) > 2 and str(row[2]).isdigit() else 1,
                    "last_read_at": row[3] if len(row) > 3 else "",
                    "group_ids": group_ids,
                }
        return None

    def upsert_progress(
        self,
        user_id: str,
        username: str,
        current_day: int,
        last_read_at: Optional[str] = None,
        group_ids: Optional[List[str]] = None,
    ) -> None:
        last_read_at = last_read_at or datetime.date.today().isoformat()
        existing = self.get_progress(user_id)
        
        # Preserve existing group_ids if not provided
        if group_ids is None:
            if existing:
                group_ids = existing.get("group_ids", [])
            else:
                group_ids = []
        
        group_ids_str = ",".join(group_ids)
        values = [str(user_id), username or "", current_day, last_read_at, group_ids_str]
        
        if existing and existing.get("row_index"):
            range_ = f"{self.sheet_name}!A{existing['row_index']}:E{existing['row_index']}"
            self.sheets_client.update_row(range_, values)
        else:
            range_ = f"{self.sheet_name}!A:E"
            self.sheets_client.append_row(range_, values)
