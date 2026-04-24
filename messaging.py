import requests

class AlertService:
    def __init__(self):
        # 🔑 Replace with your actual data from BotFather and UserInfoBot
        self.token = "YOUR_API_TOKEN"
        self.chat_id = "YOUR_CHAT_ID"

    def send_alert(self, message_body, image_path=None):
        try:
            # 1. Send Text
            text_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            response = requests.post(text_url, data={"chat_id": self.chat_id, "text": message_body}, timeout=10)
            print(f"DEBUG: Telegram Response: {response.status_code} - {response.text}")
            
            # 2. Send Photo
            if image_path:
                photo_url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
                with open(image_path, 'rb') as photo:
                    requests.post(photo_url, data={"chat_id": self.chat_id}, files={"photo": photo}, timeout=10)
            
            print("🚀 Telegram Alert Dispatched!")
        except Exception as e:
            print(f"❌ Telegram Error: {e}")
