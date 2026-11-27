import asyncio, json, os, websockets

TOKEN = os.getenv("DERIV_TOKEN")
APP_ID = 1089

async def main():
    url = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"authorize": TOKEN}))
        auth = json.loads(await ws.recv())
        print("Authorized as:", auth.get("authorize", {}).get("loginid"))
        print("Bot is running on DEMO - waiting for signal...")
        while True:
            await asyncio.sleep(10)
            print("Bot alive...")

asyncio.run(main())
