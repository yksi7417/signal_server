import json
import os
import logging
import aiohttp_cors
from aiohttp import web, WSMsgType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


clients = {} 


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    logger.info("Websocket from: %s", request.remote)
    logger.debug("Headers: %s", dict(request.headers))
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
            try:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    to_id = data.get("to")
                    if to_id in clients:
                        await clients[to_id].send_str(msg.data)
            except Exception as e:
                print("Error handling WebSocket message:", e)
    finally:
        if client_id in clients:
            del clients[client_id]
            for other_ws in clients.values():
                await other_ws.send_str(json.dumps({
                    "type": "peer-disconnect",
                    "id": client_id
                }))

    return ws


@web.middleware
async def cors_headers_middleware(request, handler):
    response = await handler(request)
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    return response


async def index_handler(request):
    return web.FileResponse('./index.html')

async def voice_handler(request):
    return web.FileResponse('./voice.html')

async def voice_command_handler(request):
    return web.FileResponse('./voice_command.html')

app = web.Application(middlewares=[cors_headers_middleware])
app.router.add_get('/', index_handler)
app.router.add_get('/voice.html', voice_handler)
app.router.add_get('/voice_command.html', voice_command_handler)
app.router.add_get('/ws', websocket_handler)
app.router.add_get('/env.js', env_js_handler)
app.router.add_static('/static/', path='./static', name='static')

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

for route in list(app.router.routes()):
    cors.add(route)

web.run_app(app, port=8080)
