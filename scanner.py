import requests, os
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def scan():
    try:
        r = requests.get("https://api.dexscreener.com/token-boosts/top/v1", timeout=15).json()
    except:
        send("⚠️ Scanner error: DexScreener down")
        return

    alerts = 0
    for t in r[:20]:
        if t.get("chainId")!= "solana":
            continue
        try:
            ca = t["tokenAddress"]
            d = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{ca}", timeout=10).json()
            p = d["pairs"][0]
            vol = float(p["volume"]["h24"] or 0)
            chg = float(p["priceChange"]["m5"] or 0)
            if vol > 10000 and chg > 20:
                alerts += 1
                send(f"🚨 *SURGE* {p['baseToken']['symbol']}\n+{chg:.1f}% (5m) | Vol ${vol:,.0f}\n`{ca}`\nhttps://dexscreener.com/solana/{ca}")
        except:
            continue

    now = datetime.utcnow().strftime("%H:%M UTC")
    if alerts == 0:
        send(f"✅ Checked {now} — No surges found\nBot is working.")
    print(f"Done. Alerts: {alerts}")

scan()
