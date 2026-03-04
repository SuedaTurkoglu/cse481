from .observer import Observer
import requests

class TelegramAlertObserver(Observer):
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        print("🔔 TelegramAlertObserver initialized.")

    def update(self, message: str):
        if "Bought" in message or "Sold" in message:
            try:
                payload = {'chat_id': self.chat_id, 'text': f"🚨 TRADE ALERT 🚨\n{message}"}
                requests.post(self.api_url, data=payload)
                print("🔔 Telegram alert sent.")
            except Exception as e:
                print(f"❌ Failed to send Telegram alert: {e}")