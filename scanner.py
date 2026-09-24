import os, requests, time

BOT = os.environ["BOT_TOKEN"]
CHAT = os.environ["CHAT_ID"]

def send_msg(text):
    requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",
        data={"chat_id": CHAT, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": False})

def send_chart(pair, text):
    # Chart preview
    chart_url = f"https://cdn.dexscreener.com/charts/solana/{pair}.png"
    # Fallback to dexscreener link if CDN fails, telegram will still show preview
    try:
        requests.post(f"https://api.telegram.org/bot{BOT}/sendPhoto",
            data={"chat_id": CHAT, "photo": chart_url, "caption": text, "parse_mode": "Markdown"}, timeout=15)
    except:
        send_msg(text)

def rug_check(mint):
    try:
        r = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{mint}/report", timeout=10).json()
        # creator holding
        creator_pct = 0
        top10_pct = 0
        if 'topHolders' in r:
            holders = r['topHolders']
            if holders:
                creator_pct = holders[0].get('pct', 0) if len(holders)>0 else 0
                top10_pct = sum(h.get('pct',0) for h in holders[:10])

        # rugcheck risks
        risks = [x for x in r.get('risks', []) if x['level'] == 'danger']

        if creator_pct > 20:
            return False, f"Dev holds {creator_pct:.1f}%"
        if top10_pct > 70:
            return False, f"Top10 holds {top10_pct:.1f}%"
        if risks:
            return False, f"Rug risk: {risks[0]['name']}"
        return True, "OK"
    except:
        return True, "RugCheck skip" # don't block if API down

# --- Your existing surge logic ---
# Example structure - keep your Dexscreener search below
try:
    res = requests.get("https://api.dexscreener.com/latest/dex/search/?q=solana", timeout=15).json()
    pairs = res.get('pairs', [])[:20]
except:
    pairs = []

found = 0
for p in pairs:
    try:
        price_change_5m = p.get('priceChange', {}).get('m5', 0)
        volume = p.get('volume', {}).get('m5', 0)
        buys = p.get('txns', {}).get('m5', {}).get('buys', 0)
        sells = p.get('txns', {}).get('m5', {}).get('sells', 0)
        mint = p.get('baseToken', {}).get('address')
        pair_addr = p.get('pairAddress')

        if price_change_5m is None: continue
        if float(price_change_5m) < 15: continue
        if volume < 10000: continue
        if buys <= sells: continue

        # NEW: Rug filter
        safe, reason = rug_check(mint)
        if not safe:
            print(f"Skipped {p['baseToken']['symbol']} - {reason}")
            continue

        found += 1
        symbol = p['baseToken']['symbol']
        msg = f"🚀 *{symbol} SURGE +{price_change_5m}% (5m)*\nVol: ${volume:,.0f} | Buys {buys} > Sells {sells}\n✅ Rug: {reason}\n[Chart](https://dexscreener.com/solana/{pair_addr})"

        send_chart(pair_addr, msg)
        time.sleep(1)

    except Exception as e:
        print(e)
        continue

if found == 0:
    from datetime import datetime
    now = datetime.utcnow().strftime("%H:%M UTC")
    send_msg(f"✅ Checked {now} — No surges found\nBot is working.")
