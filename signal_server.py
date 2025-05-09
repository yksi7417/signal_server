import asyncio
import json
from aiohttp import web, WSMsgType

clients = {}  # {id: websocket}

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("WebSocket connected from:", request.remote)

    # Default to None
    client_id = None

    # Wait for initial message (must be valid JSON with 'id')
    msg = await ws.receive()

    if msg.type == WSMsgType.TEXT:
        try:
            client_info = json.loads(msg.data)
            client_id = client_info["id"]
        except Exception as e:
            print("Invalid JSON message received:", msg.data, e)
            await ws.close()
            return ws
    else:
        print("Non-text message received:", msg.type)
        await ws.close()
        return ws

    clients[client_id] = ws

    # Notify other clients about new peer
    for other_id, other_ws in clients.items():
        if other_ws != ws:
            await other_ws.send_str(json.dumps({
                "type": "new-peer",
                "id": client_id
            }))

    # Send list of existing peers to new client
    await ws.send_str(json.dumps({
        "type": "peer-list",
        "peers": [pid for pid in clients if pid != client_id]
    }))

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    to_id = data.get("to")
                    if to_id in clients:
                        await clients[to_id].send_str(msg.data)
                except Exception as e:
                    print("Error parsing message:", msg.data, e)
    finally:
        # Cleanup on disconnect
        if client_id in clients:
            del clients[client_id]
            for other_ws in clients.values():
                await other_ws.send_str(json.dumps({
                    "type": "peer-disconnect",
                    "id": client_id
                }))

    return ws

# Aiohttp app setup
app = web.Application()
app.router.add_get('/ws', websocket_handler)
web.run_app(app, port=80)
