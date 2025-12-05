import requests
import os
from dotenv import load_dotenv

# Load .env
load_dotenv("config/.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "-1003300234495"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

def test_send_message():
    print(f"Testing text message to {CHAT_ID}...")
    resp = requests.post(f"{API_URL}/sendMessage", json={"chat_id": CHAT_ID, "text": "Test message"})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    test_send_message()
