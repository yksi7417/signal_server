# src/signaling.py

import json
import websockets
from aiortc import RTCSessionDescription
from src.config import SIGNALING_SERVER_URL, ROOM_NAME
from src.audio_handler import track_to_username

async def connect_signaling(pc):
    async with websockets.connect(SIGNALING_SERVER_URL) as ws:
        # join room
        await ws.send(json.dumps({"action": "join", "room": ROOM_NAME}))
        async for msg in ws:
            data = json.loads(msg)

            if data["type"] == "offer":
                offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                await pc.setRemoteDescription(offer)
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await ws.send(json.dumps({
                    "type": pc.localDescription.type,
                    "sdp": pc.localDescription.sdp
                }))

            elif data["type"] == "candidate":
                await pc.addIceCandidate(data["candidate"])

            elif data.get("type") == "track-metadata":
                # track‐ID → username mapping
                track_to_username[data["track_id"]] = data["username"]
