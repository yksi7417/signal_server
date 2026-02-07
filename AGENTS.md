# Agent Coding Guidelines

This document provides essential information for AI coding agents working on this signal_server project.

## Project Overview

This is a Signal Server project (mahjong game server) written in Python using:
- **aiohttp** for async web server and WebSocket handling
- **bottle** for lightweight WSGI micro framework
- **mahjong_engine** custom module for game logic

## Build/Lint/Test Commands

### Testing
```bash
# Run all tests
pytest -v

# Run unit tests only (exclude integration tests)
pytest -m "not integration" -v tests/engine

# Run integration tests only
pytest -m "integration" -v tests/integration/ -s

# Run specific test file
pytest tests/engine/test_tile.py -v

# Run specific test function
pytest tests/engine/test_tile.py::test_tile_creation -v

# Run tests by pattern (single test)
pytest -k test_tile_creation -v
```

### Linting & Formatting
```bash
# Run flake8 linting
flake8

# Run pylint
pylint mahjong_engine/

# Format with black (if installed)
black .

# Sort imports with isort (if installed)
isort .
```

### Running the Application
```bash
# Start the development server
python app.py

# Or use the batch file (Windows)
start_dev.bat
```

## Code Style Guidelines

### Imports
- Standard library imports first (e.g., `import os`, `import json`)
- Third-party imports second (e.g., `from aiohttp import web`)
- Local/project imports last (e.g., `from mahjong_engine.tile import Tile`)
- Use explicit imports, avoid `import *`
- Group imports with a blank line between each group

### Formatting
- **Line length**: 120 characters (configured in pyproject.toml and .flake8)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Single or double quotes allowed (skip-string-normalization in black)
- **Trailing whitespace**: Generally ignored by linters (see .flake8 ignore list)

### Type Hints
- Use type hints for function parameters and return values where appropriate
- Example: `async def index(request: web.Request) -> web.FileResponse:`
- Use `Optional[T]` for nullable types: `def __init__(self, player_id: int, agent: Optional[PlayerAgent] = None)`
- Use `list[T]` for typed lists (Python 3.9+)

### Naming Conventions
- **Classes**: PascalCase (e.g., `GameState`, `PlayerAgent`, `Tile`)
- **Functions/Methods**: snake_case (e.g., `test_tile_creation`, `is_terminal`)
- **Variables**: snake_case (e.g., `client_id`, `current_game_state`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `SUIT_DOTS`, `WIND_EAST`)
- **Private members**: Prefix with underscore (e.g., `self._internal_state`)

### Error Handling
- Use explicit error handling with try/except blocks
- Log errors appropriately using the `logging` module
- Use specific exception types (avoid bare `except:`)
- Example:
```python
try:
    client_info = json.loads(msg.data)
except Exception as e:
    logger.error("Invalid JSON message: %s", e)
    await ws.close()
    return ws
```

### Testing Conventions
- Test files: `test_*.py` pattern
- Test classes: `Test*` prefix
- Test functions: `test_*` prefix
- Use pytest markers: `@pytest.mark.integration` for integration tests
- Use descriptive test names explaining what is being tested
- Tests located in `tests/` directory with subdirectories for organization

### Linting Rules (from .flake8)
Following rules are ignored (do not enforce):
- E501: line too long (handled by 120 char limit instead)
- W291: trailing whitespace
- W293: blank line contains whitespace
- E302: expected 2 blank lines
- E303: too many blank lines
- E231: missing whitespace after ','
- E701: multiple statements on one line

### Pylint Rules (from .pylintrc)
Disabled rules:
- C0111: missing-docstring
- C0103: invalid-name
- R0903: too-few-public-methods
- W0511: fixme
- Line length: 160 (pylint), 120 (flake8/black)
- Max module lines: 2000

## Project Structure

```
signal_server/
├── app.py                  # Main aiohttp application
├── mahjong_engine/         # Game logic module
│   ├── tile.py            # Tile class and related logic
│   ├── player.py          # Player class
│   ├── game_state.py      # Game state management
│   ├── hand_validator.py  # Hand validation logic
│   ├── ruleset.py         # Game rules
│   ├── melds.py           # Meld (set) logic
│   ├── player_agent.py    # AI player agent
│   └── constants.py       # Game constants
├── tests/                  # Test suite
│   ├── engine/            # Unit tests for engine
│   ├── integration/       # Integration tests
│   └── websocket/         # WebSocket tests
├── static/                # Static web assets
├── audio/                 # Audio files
└── webrtc_command_server/ # WebRTC command handling
```

## Key Dependencies
- aiohttp>=3.11.18
- pytest>=8.3.3
- pytest-timeout>=2.3.1
- websockets>=15.0.1

## Notes for AI Agents
- No Cursor rules or Copilot instructions found in this repository
- This is a mahjong game server with WebSocket support for multiplayer
- The project uses async/await patterns extensively (aiohttp)
- When modifying game logic, ensure tests in tests/engine/ still pass
- Integration tests require full server setup and are marked with @pytest.mark.integration
- The project is deployed to Fly.io (see .github/workflows/deploy.yml)
