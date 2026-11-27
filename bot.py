import asyncio, json, os, sys, websockets, threading, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import deque

def log(msg):
    print(msg, flush=True)

TOKEN = os.getenv("DERIV_TOKEN")
APP_ID = 1089
PORT = int(os.getenv("PORT", 10000))
SYMBOL = "frxXAUUSD"
STAKE = 0.35

log(f"=== BOT STARTING ===")
log(f"TOKEN EXISTS: {bool(TOKEN)}")
log(f"SYMBOL: {SYMBOL}")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gold Bot Running")
    def log_message(self, *args):
        pass

def run_server():
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
threading.Thread(target=run_server, daemon=True).start()

async def send(ws, data):
    await ws.send(json.dumps(data))
    return json.loads(await ws.recv())

async def main():
    log(f"Starting Gold Scalper - {SYMBOL} Stake ${STAKE}")
    url = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"
    while True:
        try:
          async with websockets.connect(url, extra_headers={"Origin": "https://app.deriv.com", "User-Agent": "Mozilla/5.0"}) as ws:
                auth = await send(ws, {"authorize": TOKEN})
                if "error" in auth:
                    log(f"Auth failed: {auth['error']}")
                    await asyncio.sleep(10); continue
                log(f"Authorized as: {auth['authorize']['loginid']}")
                await ws.send(json.dumps({"ticks": SYMBOL, "subscribe": 1}))
                prices = deque(maxlen=50)
                last_trade = 0
                in_trade = False
                while True:
                    msg = json.loads(await ws.recv())
                    if "tick" not in msg:
                        if "proposal_open_contract" in msg:
                            c = msg["proposal_open_contract"]
                            if c.get("is_sold"):
                                log(f"TRADE RESULT: Profit ${c.get('profit')}")
                                in_trade = False
                        continue
                    price = float(msg["tick"]["quote"])
                    prices.append(price)
                    if len(prices) < 20 or in_trade:
                        continue
                    fast = sum(list(prices)[-5:]) / 5
                    slow = sum(list(prices)[-20:]) / 20
                    if time.time() - last_trade < 30:
                        continue
                    signal = "CALL" if fast > slow else "PUT"
                    log(f"Signal {signal} | Price {price} Fast {fast:.2f} Slow {slow:.2f}")
                    prop = await send(ws, {"proposal": 1, "amount": STAKE, "basis": "stake", "contract_type": signal, "currency": "USD", "duration": 5, "duration_unit": "t", "symbol": SYMBOL})
                    if "error" in prop:
                        log(f"Proposal error: {prop['error']}"); continue
                    buy = await send(ws, {"buy": prop["proposal"]["id"], "price": STAKE})
                    if "error" in buy:
                        log(f"Buy error: {buy['error']}"); continue
                    log(f"BOUGHT {signal} ID {buy['buy']['contract_id']}")
                    in_trade = True
                    last_trade = time.time()
                    await ws.send(json.dumps({"proposal_open_contract": 1, "contract_id": buy["buy"]["contract_id"], "subscribe": 1}))
        except Exception as e:
            log(f"Error: {e} - retrying in 5s...")
            await asyncio.sleep(5)

asyncio.run(main())
