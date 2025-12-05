from typing import List, Dict, Any, Optional
import datetime

from google_sheets_client import GoogleSheetsClient


class GroupRepository:
    """Load group configurations from a Google Sheet.

    Expected columns (with header in row 1):
    chat_id | plan_sheet | start_date (YYYY-MM-DD) | timezone
    """

    def __init__(self, sheets_client: GoogleSheetsClient, sheet_name: str) -> None:
        self.sheets_client = sheets_client
        self.sheet_name = sheet_name

    def list_groups(self) -> List[Dict[str, Any]]:
        range_ = f"{self.sheet_name}!A2:D"
        rows = self.sheets_client.get_values(range_)
        groups: List[Dict[str, Any]] = []
        for row in rows:
            if not row or not row[0]:
                continue
            chat_id = str(row[0]).strip()
            plan_sheet = row[1].strip() if len(row) > 1 and row[1] else None
            start_date = self._parse_date(row[2]) if len(row) > 2 and row[2] else None
            timezone = row[3].strip() if len(row) > 3 and row[3] else None
            notification_time = row[4].strip() if len(row) > 4 and row[4] else "08:00"
            groups.append(
                {
                    "chat_id": chat_id,
                    "plan_sheet": plan_sheet,
                    "start_date": start_date,
                    "timezone": timezone,
                    "notification_time": notification_time,
                }
            )
        return groups

    @staticmethod
    def _parse_date(value: str) -> Optional[datetime.date]:
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return None

    def append_group(
        self,
        chat_id: str,
        plan_sheet: Optional[str],
        start_date: Optional[datetime.date],
        timezone: Optional[str],
        notification_time: str = "08:00",
    ) -> None:
        plan_sheet = plan_sheet or ""
        start_date_str = start_date.isoformat() if start_date else ""
        tz = timezone or ""
        range_ = f"{self.sheet_name}!A:E"
        self.sheets_client.append_row(range_, [chat_id, plan_sheet, start_date_str, tz, notification_time])

    def update_start_date(self, chat_id: str, new_date: datetime.date) -> bool:
        """Update the start_date for a given chat_id."""
        # 1. Find the row index
        range_ = f"{self.sheet_name}!A2:A" # Read only chat_ids
        rows = self.sheets_client.get_values(range_)
        
        row_index = -1
        for idx, row in enumerate(rows):
            if row and str(row[0]).strip() == str(chat_id):
                row_index = idx + 2 # +2 because 0-based index + 1 header row + 1 for 1-based sheet
                break
        
        if row_index == -1:
            return False
            
        # 2. Update the cell (Column C is start_date)
        cell_range = f"{self.sheet_name}!C{row_index}"
        self.sheets_client.update_row(cell_range, [new_date.isoformat()])
        return True

    def update_notification_time(self, chat_id: str, new_time: str) -> bool:
        """Update the notification_time for a given chat_id."""
        # 1. Find the row index
        range_ = f"{self.sheet_name}!A2:A"
        rows = self.sheets_client.get_values(range_)
        
        row_index = -1
        for idx, row in enumerate(rows):
            if row and str(row[0]).strip() == str(chat_id):
                row_index = idx + 2
                break
        
        if row_index == -1:
            return False
            
        # 2. Update the cell (Column E is notification_time)
        cell_range = f"{self.sheet_name}!E{row_index}"
        self.sheets_client.update_row(cell_range, [new_time])
        return True
