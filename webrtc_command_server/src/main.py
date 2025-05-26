# src/main.py

import asyncio
from aiortc import RTCPeerConnection
from src.signaling import connect_signaling
from src.audio_handler import handle_audio_track

async def run():
    pc = RTCPeerConnection()

    @pc.on("track")
    def on_track(track):

        asyncio.create_task(handle_audio_track(track))


    await connect_signaling(pc)
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(run())
