import asyncio
import websockets
import json
import random
import string


def random_id(prefix="client", length=4):
    suffix = ''.join(random.choices(string.digits, k=length))
    return f"{prefix}-{suffix}"


async def test():
    uri = "ws://localhost:8080/ws"  # Change to wss://yourdomain if needed
    async with websockets.connect(uri) as websocket:
        # Send handshake message
        my_id = random_id()
        await websocket.send(json.dumps({
            "type": "hello",
            "id": my_id
        }))
        print("✅ Sent hello handshake")

        # Listen for peer-list or new-peer responses
        while True:
            msg = await websocket.recv()
            print("📨 Received:", msg)

asyncio.run(test())
