# src/config.py

# Signaling
SIGNALING_SERVER_URL = "ws://localhost:8000/ws"
ROOM_NAME = "voice-room"

# VAD aggressiveness (0–3)
VAD_AGGRESSIVENESS = 2

# STT (Whisper.cpp via pywhispercpp)
WHISPER_MODEL = "medium"        

# Command parser (llama.cpp)
COMMAND_MODEL_PATH = "models/command-parser.gguf"
LLM_N_GPU_LAYERS = 30         
LLM_GPU_LAYERS = [0, 1]       

# Allowed commands
COMMAND_LIST = [
    "play",
    "pause",
    "skip",
    "stop",
    "volume up",
    "volume down"
]

track_to_username = {} 