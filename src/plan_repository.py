import re
import logging
from typing import Optional, Dict, Any, List

import constants
from google_sheets_client import GoogleSheetsClient


class PlanRepository:
    def __init__(self, sheets_client: GoogleSheetsClient, sheet_name: str) -> None:
        self.sheets_client = sheets_client
        self.sheet_name = sheet_name
        self.cache: Dict[int, Dict[str, Any]] = {}
        self.reload()

    def reload(self) -> None:
        """Load all plan data from Google Sheets into memory using header mapping."""
        self.cache.clear()
        # Fetch A1:Z to include headers and potential extra columns
        range_ = f"{self.sheet_name}!A1:Z"
        rows = self.sheets_client.get_values(range_)
        if not rows:
            logging.warning("Plan sheet '%s' is empty.", self.sheet_name)
            return

        headers = [h.strip() for h in rows[0]]
        data_rows = rows[1:]

        # Map column names to indices
        col_map = {name: i for i, name in enumerate(headers)}
        
        # Helper to safely get value by column name
        def get_val(row: List[str], col_name: str) -> str:
            idx = col_map.get(col_name)
            if idx is not None and idx < len(row):
                return row[idx]
            return ""

        for row in data_rows:
            if not row:
                continue
            try:
                # Day column is required
                raw_day = get_val(row, constants.COL_DAY).strip()
                if not raw_day:
                    # Fallback: try first column if 'Day' header missing or empty
                    if len(row) > 0:
                        raw_day = row[0]
                
                match = re.search(r"\d+", raw_day)
                if not match:
                    continue
                row_day = int(match.group(0))
                
                self.cache[row_day] = {
                    "day": row_day,
                    "ref": get_val(row, constants.COL_REF),
                    "title": get_val(row, constants.COL_TITLE),
                    "summary": get_val(row, constants.COL_SUMMARY),
                    "verse_text": get_val(row, constants.COL_VERSE_TEXT),
                    "verse_ref": get_val(row, constants.COL_VERSE_REF),
                    "image_url": get_val(row, constants.COL_IMAGE_URL),
                    "youtube_link": get_val(row, constants.COL_YOUTUBE_LINK),
                    "mt": get_val(row, constants.COL_MT),
                    "mk": get_val(row, constants.COL_MK),
                    "lk": get_val(row, constants.COL_LK),
                }
            except (ValueError, IndexError):
                continue

    def get_plan_by_day(self, day: int) -> Optional[Dict[str, Any]]:
        """Return plan row for given day from cache."""
        return self.cache.get(day)

