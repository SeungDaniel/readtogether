from typing import List, Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetsClient:
    def __init__(self, spreadsheet_id: str, credentials_file: str) -> None:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=SCOPES
        )
        self._service = build("sheets", "v4", credentials=credentials)
        self.spreadsheet_id = spreadsheet_id

    def get_values(self, range_: str) -> List[List[Any]]:
        """Fetch values for a given A1 range; returns empty list on errors."""
        try:
            response = (
                self._service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=range_)
                .execute()
            )
            return response.get("values", [])
        except HttpError:
            return []

    def append_row(self, range_: str, row_values: List[Any]) -> None:
        """Append a single row to the specified range."""
        self._service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [row_values]},
        ).execute()

    def update_row(self, range_: str, row_values: List[Any]) -> None:
        """Update a range (typically a full row) with new values."""
        self._service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_,
            valueInputOption="RAW",
            body={"values": [row_values]},
        ).execute()
