import asyncio
import json
from aiohttp import web, WSMsgType

clients = {}  # {id: websocket}

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Wait for the client to send its ID
    msg = await ws.receive()
    client_info = json.loads(msg.data)
    client_id = client_info["id"]
    clients[client_id] = ws

    # Notify all other clients about the new peer
    for other_id, other_ws in clients.items():
        if other_ws != ws:
            await other_ws.send_str(json.dumps({
                "type": "new-peer",
                "id": client_id
            }))

    # Send list of existing peers to this new client
    await ws.send_str(json.dumps({
        "type": "peer-list",
        "peers": [pid for pid in clients if pid != client_id]
    }))

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                to_id = data.get("to")
                if to_id in clients:
                    await clients[to_id].send_str(msg.data)
    finally:
        del clients[client_id]
        for other_ws in clients.values():
            await other_ws.send_str(json.dumps({
                "type": "peer-disconnect",
                "id": client_id
            }))

    return ws

app = web.Application()
app.router.add_get('/ws', websocket_handler)
web.run_app(app, port=8080)
