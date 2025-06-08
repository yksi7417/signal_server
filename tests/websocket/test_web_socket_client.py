import asyncio
import websockets
import json
import random
import string


def random_id(prefix="client", length=4):
    suffix = ''.join(random.choices(string.digits, k=length))
    return f"{prefix}-{suffix}"


async def test():
    uri = "wss://oracle-free-instance-20230330-1941.tail356fe.ts.net/ws"
    async with websockets.connect(uri) as websocket:

        my_id = random_id()
        await websocket.send(json.dumps({
            "type": "hello",
            "id": my_id
        }))
        print("✅ Sent hello handshake")


        while True:
            msg = await websocket.recv()
            print("📨 Received:", msg)

asyncio.run(test())
