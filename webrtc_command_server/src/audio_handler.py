# src/audio_handler.py

import webrtcvad
from aiortc import AudioStreamTrack
from src.config import VAD_AGGRESSIVENESS, track_to_username
from src.stt import transcribe
from src.classifier import classify_command

vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

async def handle_audio_track(track: AudioStreamTrack):
    buffer = bytearray()
    sample_rate = 48000

    async for frame in track.recv():
        pcm = frame.to_ndarray().tobytes()
        if vad.is_speech(pcm, sample_rate):
            buffer.extend(pcm)
        else:
            if buffer:
                text = transcribe(bytes(buffer), sample_rate)
                await classify_command(track.id, text)
                buffer.clear()
