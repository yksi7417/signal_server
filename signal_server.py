import json
import os
import logging
from flask import Flask, Response, send_from_directory, request
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path="/static", static_folder="static")

WS_ENDPOINTS = {
    "dev": "ws://localhost:8080/ws",
    "uat": "wss://oracle-free-instance-20230330-1941.tail356fe.ts.net/ws",
    "prod": "wss://signal-server-eo-7uq.fly.dev/ws"
}


def env_js_handler():
    env = os.getenv("APP_ENV", "prod").lower().strip()
    ws_url = WS_ENDPOINTS.get(env, WS_ENDPOINTS["prod"])

    js_code = (
        f"window.APP_CONFIG = {{\n  env: \"{env}\",\n  wsUrl: \"{ws_url}\"\n}};"
    )

    return Response(js_code, mimetype="application/javascript")


clients = {}


def websocket_handler():
    ws = request.environ.get("wsgi.websocket")
    if ws is None:
        return "WebSocket connection expected", 400

    logger.info("Websocket from: %s", request.remote_addr)
    logger.debug("Headers: %s", dict(request.headers))
    print("Cookies:", request.cookies)

    client_id = None

    msg = ws.receive()
    if msg is not None:
        try:
            client_info = json.loads(msg)
            client_id = client_info["id"]
        except Exception as e:
            print("Invalid JSON message received:", msg, e)
            ws.close()
            return ""
    else:
        ws.close()
        return ""

    clients[client_id] = ws


    for other_id, other_ws in clients.items():
        if other_ws != ws:
            try:
                other_ws.send(json.dumps({"type": "new-peer", "id": client_id}))
            except Exception:
                pass

    ws.send(json.dumps({
        "type": "peer-list",
        "peers": [pid for pid in clients if pid != client_id]
    }))

    try:
        while True:
            msg = ws.receive()
            if msg is None:
                break
            try:
                data = json.loads(msg)
                to_id = data.get("to")
                if to_id in clients:
                    clients[to_id].send(msg)
            except Exception as e:
                print("Error handling WebSocket message:", e)
    finally:
        if client_id in clients:
            del clients[client_id]
            for other_ws in clients.values():
                try:
                    other_ws.send(json.dumps({"type": "peer-disconnect", "id": client_id}))
                except Exception:
                    pass

    return ""

@app.after_request
def add_security_headers(response):
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response


@app.route("/")
def index_handler():
    return send_from_directory(".", "index.html")


@app.route("/voice.html")
def voice_handler():
    return send_from_directory(".", "voice.html")


@app.route("/voice_command.html")
def voice_command_handler():
    return send_from_directory(".", "voice_command.html")


app.add_url_rule("/ws", view_func=websocket_handler)
app.add_url_rule("/env.js", view_func=env_js_handler)


if __name__ == "__main__":
    server = pywsgi.WSGIServer(("", 8080), app, handler_class=WebSocketHandler)
    server.serve_forever()

