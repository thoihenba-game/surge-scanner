import os, requests
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

send("✅ *Surge Scanner is live!* \nBot connected successfully. You will get alerts every 15 min on volume surges.")
print("Sent test message")
