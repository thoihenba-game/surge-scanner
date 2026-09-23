import requests, os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def check():
    # Latest boosted/new tokens
    r = requests.get("https://api.dexscreener.com/token-boosts/top/v1", timeout=15).json()
    alerts = []
    for t in r[:30]:
        try:
            # Get pair details
            addr = t.get("tokenAddress")
            chain = t.get("chainId")
            # filter example: Solana only for speed
            if chain not in ["solana", "ethereum", "bsc"]: continue
            # You can add more filters here: check dexscreener page
            # For v1, we use boost amount as proxy for interest
            alerts.append(f"*{t.get('description','New')}*\nChain: {chain}\n`{addr}`\nhttps://dexscreener.com/{chain}/{addr}")
        except: continue
    
    # Simple dedup: only alert top 3 to avoid spam in test
    if alerts:
        send("🚨 *New Surge Candidates:*\n\n" + "\n\n".join(alerts[:3]))

if __name__ == "__main__":
    check()
