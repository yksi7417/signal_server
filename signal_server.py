import json
import os
from pprint import pprint
from aiohttp import web, WSMsgType

WS_ENDPOINTS = {
    "dev": "ws://localhost:8080/ws",
    "uat": "wss://oracle-free-instance-20230330-1941.tail356fe.ts.net/ws",
    "prod": "wss://signal-server-eo-7uq.fly.dev/ws"
}


async def env_js_handler(request):
    env = os.getenv("APP_ENV", "prod").lower().strip()
    ws_url = WS_ENDPOINTS.get(env, WS_ENDPOINTS["prod"])

    js_code = f"""
    window.APP_CONFIG = {{
      env: "{env}",
      wsUrl: "{ws_url}"
    }};
    """.strip()

    return web.Response(text=js_code, content_type="application/javascript")


clients = {}  # {id: websocket}


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("Websocket from:", request.remote)
    pprint(dict(request.headers))
    print("Cookies:", request.cookies)

    client_id = None

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

    # Notify others
    for other_id, other_ws in clients.items():
        if other_ws != ws:
            await other_ws.send_str(json.dumps({
                "type": "new-peer",
                "id": client_id
            }))

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
        if client_id in clients:
            del clients[client_id]
            for other_ws in clients.values():
                await other_ws.send_str(json.dumps({
                    "type": "peer-disconnect",
                    "id": client_id
                }))

    return ws


async def index_handler(request):
    return web.FileResponse('./index.html')

app = web.Application()
app.router.add_get('/', index_handler)
app.router.add_get('/ws', websocket_handler)
app.router.add_get('/env.js', env_js_handler)
app.router.add_static('/static/', path='./static', name='static')

web.run_app(app, port=8080)
