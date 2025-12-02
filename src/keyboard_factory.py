from typing import Dict, Any

def get_quest_keyboard() -> Dict[str, Any]:
    """Return the standard inline keyboard for quest messages."""
    return {
        "inline_keyboard": [
            [
                {"text": "✅ 읽음 완료 (다음으로)", "callback_data": "next"}
            ],
            [
                {"text": "📖 다시 읽기", "callback_data": "repeat"},
                {"text": "📊 내 현황", "callback_data": "status"}
            ]
        ]
    }

def get_start_keyboard() -> Dict[str, Any]:
    """Return the welcome keyboard."""
    return {
        "inline_keyboard": [
            [{"text": "🚀 1일차 시작하기", "callback_data": "next"}]
        ]
    }

def get_group_read_keyboard() -> Dict[str, Any]:
    """Return the 'Read' button for group messages."""
    return {
        "inline_keyboard": [
            [{"text": "✅ 아멘 / 읽음", "callback_data": "group_read"}]
        ]
    }
