# WebRTC Voice Command Server

## Setup

1. **Clone** this repo.
2. **Download** Whisper & command-parser models into `models/`.
3. **Configure** `src/config.py` with your signaling URL, model paths, GPU settings, and command list.
4. **Create** a virtualenv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

# not working yet - latest chat progress is 
https://chatgpt.com/c/6822ab35-52ac-8003-8630-c91e8c17cf42