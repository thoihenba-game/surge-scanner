import os
import requests
import time
from datetime import datetime, timezone

BOT = os.environ["BOT_TOKEN"]
CHAT = os.environ["CHAT_ID"]

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT}/sendMessage",
        data={"chat_id": CHAT, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": True},
        timeout=15
    )

def get_pairs():
    try:
        r = requests.get("https://api.dexscreener.com/latest/dex/search/?q=solana", timeout=15).json()
        return r.get('pairs', [])[:50]
    except Exception:
        return []

now = datetime.now(timezone.utc).strftime("%H:%M UTC")
pairs = get_pairs()
found = 0

for p in pairs:
    try:
        if p.get('chainId') != 'solana':
            continue

        liq = float(p.get('liquidity', {}).get('usd', 0) or 0)
        if liq < 5000:
            continue

        m5 = p.get('priceChange', {}).get('m5', 0)
        try:
            m5_val = float(m5)
        except:
            continue
        if m5_val < 15:
            continue

        tx = p.get('txns', {}).get('m5', {})
        buys = tx.get('buys', 0)
        sells = tx.get('sells', 0)
        total_tx = buys + sells
        if total_tx < 15:
            continue
        if buys <= sells:
            continue

        vol_m5 = float(p.get('volume', {}).get('m5', 0) or 0)
        if vol_m5 < 5000:
            continue

        created = p.get('pairCreatedAt', 0) or 0
        age_ms = int(time.time() * 1000) - int(created)
        age_min = age_ms / 60000
        if age_min < 10 or age_min > 360:
            continue

        name = p.get('baseToken', {}).get('name', 'Unknown')
        symbol = p.get('baseToken', {}).get('symbol', '')
        price = p.get('priceUsd', '?')
        url = p.get('url', '')

        msg = f"🚀 *SURGE ALERT*\n\n*{name} (${symbol})*\n+{m5_val}% (5m) | Vol ${vol_m5:,.0f}\nBuys {buys} / Sells {sells} | Liq ${liq:,.0f}\nPrice: ${price}\nAge: {int(age_min)}m\n{url}"
        send(msg)
        found += 1
        time.sleep(1)
        if found >= 3:
            break
    except Exception:
        continue

if found == 0:
    send(f"✅ Checked {now} — No real surges found\nFiltered {len(pairs)} pairs. Bot is working.")

print(f"Done. Found {found}")
