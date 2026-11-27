import asyncio, json, os, websockets, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.getenv("DERIV_TOKEN")
APP_ID = 1089
PORT = int(os.getenv("PORT", 10000))

# Fake web server so Render sees an open port
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")
    def log_message(self, *args):
        pass

def run_server():
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()
print(f"Web server started on port {PORT}")

async def main():
    print(f"Token loaded? {bool(TOKEN)}")
    if not TOKEN:
        print("ERROR: DERIV_TOKEN missing!")
        return
    url = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"
    while True:
        try:
            print("Connecting to Deriv...")
            async with websockets.connect(url) as ws:
                await ws.send(json.dumps({"authorize": TOKEN}))
                auth = json.loads(await ws.recv())
                if "error" in auth:
                    print("Authorize FAILED:", auth["error"])
                    await asyncio.sleep(10)
                    continue
                print("Authorized as:", auth.get("authorize", {}).get("loginid"))
                print("Bot is running - waiting for signal...")
                while True:
                    await asyncio.sleep(10)
                    print("Bot alive...")
        except Exception as e:
            print(f"Connection failed: {e} - retrying in 5s...")
            await asyncio.sleep(5)

asyncio.run(main())
