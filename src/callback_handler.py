# Webhook Callback Handler for Bible Reading Bot
# 텔레그램 Webhook을 통해 읽음 인증 버튼 클릭을 처리합니다.
#
# 실행 방법:
# 1. 직접 실행: python callback_handler.py (Flask 서버로 실행)
# 2. 환경변수: WEBHOOK_PORT (기본값: 8443)
#
# Telegram Webhook 설정:
# curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-domain.com/webhook"

import datetime
import logging
import os
import json
from typing import Optional

from flask import Flask, request, jsonify
import requests

import config
from google_sheets_client import GoogleSheetsClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = Flask(__name__)

# Sheet name for confirmations
CONFIRMATIONS_SHEET = "confirmations"


def answer_callback_query(callback_query_id: str, text: str = "") -> None:
    """Acknowledge a callback query to stop the loading animation."""
    url = f"{config.TELEGRAM_API_BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
        payload["show_alert"] = False
    try:
        requests.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)
    except Exception:
        logging.warning("Failed to answer callback query", exc_info=True)


def log_read_confirmation(
    sheets_client: GoogleSheetsClient,
    user_id: str,
    username: str,
    chat_id: str,
    book_id: str,
    day: int
) -> None:
    """Log read confirmation to Google Sheets."""
    timestamp = datetime.datetime.now().isoformat()
    values = [timestamp, user_id, username, chat_id, book_id, str(day)]
    range_ = f"{CONFIRMATIONS_SHEET}!A:F"
    try:
        sheets_client.append_row(range_, values)
        logging.info("Logged confirmation: user=%s, book=%s, day=%s", user_id, book_id, day)
    except Exception:
        logging.error("Failed to log confirmation", exc_info=True)


def handle_callback_query(callback_query: dict, sheets_client: GoogleSheetsClient) -> str:
    """Handle callback query from inline button click."""
    callback_id = callback_query.get("id")
    data = callback_query.get("data", "")
    user = callback_query.get("from", {})
    
    user_id = str(user.get("id", ""))
    username = user.get("username", "") or user.get("first_name", "Unknown")
    
    if not data.startswith("read:"):
        answer_callback_query(callback_id, "알 수 없는 요청입니다.")
        return "unknown"
    
    try:
        # Parse: read:{book_id}:{day}:{chat_id}
        parts = data.split(":")
        if len(parts) >= 4:
            book_id = parts[1]
            day = int(parts[2])
            chat_id = parts[3]
        else:
            raise ValueError("Invalid callback data format")
    except (ValueError, IndexError) as e:
        logging.warning("Invalid callback data: %s", data)
        answer_callback_query(callback_id, "오류가 발생했습니다.")
        return "error"
    
    # Log to Google Sheets
    log_read_confirmation(sheets_client, user_id, username, chat_id, book_id, day)
    
    # Send response
    answer_callback_query(callback_id, f"✅ DAY {day} 읽음 인증 완료!")
    
    return "ok"


@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhook from Telegram."""
    try:
        update = request.get_json()
        logging.debug("Received update: %s", json.dumps(update, ensure_ascii=False))
        
        # Only handle callback_query
        if "callback_query" in update:
            sheets_client = GoogleSheetsClient(
                spreadsheet_id=config.SPREADSHEET_ID,
                credentials_file=config.GOOGLE_SERVICE_ACCOUNT_FILE,
            )
            result = handle_callback_query(update["callback_query"], sheets_client)
            return jsonify({"status": result})
        
        return jsonify({"status": "ignored"})
    
    except Exception as e:
        logging.error("Webhook error: %s", e, exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


def main():
    """Run Flask server."""
    port = int(os.environ.get("WEBHOOK_PORT", "8443"))
    logging.info("Starting webhook server on port %s", port)
    
    # In production, use gunicorn or similar:
    # gunicorn -w 2 -b 0.0.0.0:8443 callback_handler:app
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
