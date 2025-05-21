# src/stt.py

import numpy as np
import resampy
from pywhispercpp.model import Model
from src.config import WHISPER_MODEL

# load once at startup
_stt = Model(WHISPER_MODEL)

def transcribe(pcm_bytes: bytes, sample_rate: int = 48000) -> str:
    # int16 PCM → float32 in [-1,1]
    audio_int16 = np.frombuffer(pcm_bytes, dtype=np.int16)
    audio = audio_int16.astype(np.float32) / 32768.0

    # resample to 16 kHz if needed
    if sample_rate != 16000:
        audio = resampy.resample(audio, sample_rate, 16000)

    # run whisper.cpp transcription
    segments = _stt.transcribe(audio)
    return " ".join(seg.text for seg in segments)
