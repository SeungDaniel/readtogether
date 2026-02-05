# Book Registry - Multi-book support for Bible Reading Bot
# 성경책 메타데이터 레지스트리

from typing import Dict, Any, Optional, List

BOOKS: Dict[str, Dict[str, Any]] = {
    "john": {
        "id": "john",
        "name_ko": "요한복음",
        "name_en": "John",
        "total_days": 66,
        "sheet_name": "plan",  # 기존 시트명 유지
        "game_link": "https://john.rtl.kr/",
        "emoji": "📖",
    },
    "isaiah": {
        "id": "isaiah",
        "name_ko": "이사야",
        "name_en": "Isaiah",
        "total_days": 94,
        "sheet_name": "plan_isaiah",
        "game_link": "",
        "emoji": "📜",
    },
}

DEFAULT_BOOK = "john"


def get_book(book_id: str) -> Dict[str, Any]:
    """Get book metadata by ID. Falls back to default if not found."""
    return BOOKS.get(book_id, BOOKS[DEFAULT_BOOK])


def list_books() -> List[Dict[str, Any]]:
    """Return list of all available books."""
    return list(BOOKS.values())


def get_book_by_sheet(sheet_name: str) -> Optional[Dict[str, Any]]:
    """Find book by sheet name."""
    for book in BOOKS.values():
        if book["sheet_name"] == sheet_name:
            return book
    return None
