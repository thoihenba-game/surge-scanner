import requests, os, time

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def scan():
    # Get trending Solana pairs from DexScreener
    try:
        r = requests.get("https://api.dexscreener.com/token-boosts/top/v1", timeout=15).json()
    except:
        return

    alerts = 0
    for t in r[:20]: # top 20 boosted
        if t.get("chainId")!= "solana":
            continue

        # Get pair details
        try:
            addr = t.get("tokenAddress")
            d = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{addr}", timeout=15).json()
            pairs = d.get("pairs", [])
            if not pairs: continue
            p = pairs[0]

            vol5 = p.get("volume", {}).get("m5", 0)
            vol1h = p.get("volume", {}).get("h1", 0)
            price_chg = p.get("priceChange", {}).get("m5", 0)
            liq = p.get("liquidity", {}).get("usd", 0)

            # Surge filter: high 5m volume + positive momentum
            if vol5 > 10000 and price_chg > 20 and liq > 20000:
                symbol = p.get("baseToken", {}).get("symbol", "???")
                price = p.get("priceUsd", "0")
                dex = p.get("dexId", "")

                msg = f"🚨 *SURGE: ${symbol}*\nPrice: ${price} (+{price_chg:.1f}% 5m)\nVol 5m: ${vol5:,.0f}\nVol 1h: ${vol1h:,.0f}\nLiq: ${liq:,.0f}\nDEX: {dex}\n`{addr}`"
                send(msg)
                alerts += 1
                time.sleep(1)
                if alerts >= 3: break
        except:
            continue

    if alerts == 0:
        print("No surges found")

scan()
