import asyncio, json, os, websockets

TOKEN = os.getenv("DERIV_TOKEN")
APP_ID = 1089

async def main():
    print(f"Token loaded? {bool(TOKEN)} Length: {len(TOKEN) if TOKEN else 0}")
    if not TOKEN:
        print("ERROR: DERIV_TOKEN missing in Render Environment!")
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
