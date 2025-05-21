# src/classifier.py

import json
from llama_cpp import Llama
from src.config import (
    COMMAND_MODEL_PATH,
    LLM_N_GPU_LAYERS,
    LLM_GPU_LAYERS,
    COMMAND_LIST,
    track_to_username
)

# instantiate once, split layers across GPUs
_llm = Llama(
    model_path=COMMAND_MODEL_PATH,
    n_gpu_layers=LLM_N_GPU_LAYERS,
    gpu_layers=LLM_GPU_LAYERS
)

async def classify_command(track_id: str, transcript: str):
    username = track_to_username.get(track_id, "unknown")
    cmds = ", ".join(f'"{c}"' for c in COMMAND_LIST)
    prompt = (
        f'User "{username}" said: "{transcript}"\n'
        f"Choose one of [{cmds}]. Reply with exactly the command or 'none'."
    )
    resp = _llm(prompt, max_tokens=8, stop=["\n"])
    command = resp["choices"][0]["text"].strip()
    output = {"username": username, "command": command, "raw": transcript}
    print(json.dumps(output, ensure_ascii=False))
