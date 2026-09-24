import os, requests, time
from datetime import datetime, timezone

BOT = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT = os.environ["TELEGRAM_CHAT_ID"]

def send(msg):
    requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",
        data={"chat_id": CHAT, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": True})

def get_pairs():
    # trending solana pairs - free, no key
    try:
        r = requests.get("https://api.dexscreener.com/latest/dex/search/?q=solana", timeout=15).json()
        return r.get('pairs', [])[:50]
    except:
        return []

now = datetime.now(timezone.utc).strftime("%H:%M UTC")
pairs = get_pairs()
found = 0

for p in pairs:
    try:
        if p.get('chainId') != 'solana': continue
        
        # Filters to kill fake pumps like INU TOWN
        liq = float(p.get('liquidity', {}).get('usd', 0) or 0)
        if liq < 5000: continue  # must have real liquidity

        m5 = p.get('priceChange', {}).get('m5', 0)
        if m5 < 15: continue  # surge at least +15% in 5m

        tx = p.get('txns', {}).get('m5', {})
        buys = tx.get('buys', 0)
        sells = tx.get('sells', 0)
        total_tx = buys + sells
        if total_tx < 15: continue  # too quiet
        if buys <= sells: continue  # we want more buys than sells - INU TOWN was 1 vs 5

        vol_m5 = float(p.get('volume', {}).get('m5', 0) or 0)
        if vol_m5 < 5000: continue  # $62 volume like INU TOWN now will be skipped

        age_ms
