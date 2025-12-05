import re
from typing import Optional, Tuple

def convert_google_drive_url(url: str) -> str:
    """Convert Google Drive viewer URL to direct download URL."""
    # Pattern to match /file/d/{FILE_ID}/...
    match = re.search(r"/file/d/([^/]+)", url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?id={file_id}"
    return url

def parse_chat_destination(chat_id_str: str) -> Tuple[str, Optional[int]]:
    """Allow chat ids like '-100123_456' where 456 is a topic/thread id."""
    match = re.match(r"(?P<chat>-?\d+)(?:_(?P<thread>\d+))?$", chat_id_str.strip())
    if match:
        chat = match.group("chat")
        thread = match.group("thread")
        return chat, int(thread) if thread else None
    return chat_id_str, None
