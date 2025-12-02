import re
from typing import Optional, Dict, Any, List

from google_sheets_client import GoogleSheetsClient


class PlanRepository:
    def __init__(self, sheets_client: GoogleSheetsClient, sheet_name: str) -> None:
        self.sheets_client = sheets_client
        self.sheet_name = sheet_name
        self.cache: Dict[int, Dict[str, Any]] = {}
        self.reload()

    def reload(self) -> None:
        """Load all plan data from Google Sheets into memory."""
        self.cache.clear()
        range_ = f"{self.sheet_name}!A2:G"
        rows = self.sheets_client.get_values(range_)
        if not rows:
            return

        for row in rows:
            if not row:
                continue
            try:
                raw_day = str(row[0]).strip()
                match = re.search(r"\d+", raw_day)
                if not match:
                    continue
                row_day = int(match.group(0))
                
                self.cache[row_day] = {
                    "day": row_day,
                    "ref": row[1] if len(row) > 1 else "",
                    "title": row[2] if len(row) > 2 else "",
                    "summary": row[3] if len(row) > 3 else "",
                    "verse_text": row[4] if len(row) > 4 else "",
                    "verse_ref": row[5] if len(row) > 5 else "",
                    "image_url": row[6] if len(row) > 6 else "",
                }
            except (ValueError, IndexError):
                continue

    def get_plan_by_day(self, day: int) -> Optional[Dict[str, Any]]:
        """Return plan row for given day from cache."""
        return self.cache.get(day)

