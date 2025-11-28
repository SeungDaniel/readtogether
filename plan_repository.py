import re
from typing import Optional, Dict, Any, List

from google_sheets_client import GoogleSheetsClient


class PlanRepository:
    def __init__(self, sheets_client: GoogleSheetsClient, sheet_name: str) -> None:
        self.sheets_client = sheets_client
        self.sheet_name = sheet_name

    def _rows(self) -> List[List[Any]]:
        range_ = f"{self.sheet_name}!A2:D"
        return self.sheets_client.get_values(range_)

    def get_plan_by_day(self, day: int) -> Optional[Dict[str, Any]]:
        """Return plan row for given day as dict."""
        rows = self._rows()
        for row in rows:
            if not row:
                continue
            try:
                raw_day = str(row[0]).strip()
                # allow formats like "1" or "1일차" by extracting leading digits
                match = re.search(r"\d+", raw_day)
                if not match:
                    continue
                row_day = int(match.group(0))
            except (ValueError, IndexError):
                continue
            if row_day == day:
                return {
                    "day": row_day,
                    "ref": row[1] if len(row) > 1 else "",
                    "title": row[2] if len(row) > 2 else "",
                    "summary": row[3] if len(row) > 3 else "",
                }
        return None
