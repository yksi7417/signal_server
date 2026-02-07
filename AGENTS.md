# Agents Operational Guide

This file documents how to build, test, and run the Signal Server project.

Last updated: {{ timestamp }}

## Project Overview

High-performance mahjong game server with WebSocket support for multiplayer gameplay.

- **Language**: Python 3.9+
- **Framework**: aiohttp (async web server)
- **Testing**: pytest
- **Architecture**: Clean separation between game engine and server logic

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment recommended

## Project Structure

```
signal_server/
├── app.py                  # Main aiohttp application entry point
├── mahjong_engine/         # Game logic module (transport-agnostic)
│   ├── tile.py            # Tile class and related logic
│   ├── player.py          # Player class
│   ├── game_state.py      # Game state management
│   ├── hand_validator.py  # Hand validation logic
│   ├── ruleset.py         # Game rules
│   ├── melds.py           # Meld (set) logic
│   ├── player_agent.py    # AI player agent
│   └── constants.py       # Game constants
├── tests/                  # Test suite
│   ├── engine/            # Unit tests for game engine
│   ├── integration/       # Integration tests (require server)
│   └── websocket/         # WebSocket-specific tests
├── static/                # Static web assets (HTML, CSS, JS)
├── audio/                 # Audio files for voice commands
├── webrtc_command_server/ # WebRTC command handling
├── pyproject.toml         # Project configuration (pytest, black, isort)
├── .flake8               # Flake8 linting configuration
└── .pylintrc             # Pylint configuration
```

## How to Build

```bash
# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## How to Test

### Run All Tests
```bash
# Run complete test suite
pytest -v
```

### Run Specific Test Types
```bash
# Run unit tests only (fast, no server required)
pytest -m "not integration" -v tests/engine

# Run integration tests only (requires server running)
pytest -m "integration" -v tests/integration/ -s

# Run WebSocket tests
pytest -v tests/websocket/
```

### Run Single Tests
```bash
# Run specific test file
pytest tests/engine/test_tile.py -v

# Run specific test class
pytest tests/engine/test_tile.py::TestTile -v

# Run specific test function
pytest tests/engine/test_tile.py::test_tile_creation -v

# Run tests matching a pattern
pytest -k test_tile -v
```

### Docker-Based Integration Tests

**Pre-commit Testing**: Before checking in code, run the full integration test suite in Docker to ensure gameplay follows mahjong rules.

```bash
# Run all integration tests in Docker (recommended before commits)
cd tests/integration
./run-integration-tests.sh

# Or manually with docker-compose
cd tests/integration
docker-compose -f docker-compose.integration.yml up --build

# Run specific test suite in Docker
docker-compose -f docker-compose.integration.yml exec -T test-runner \
  pytest tests/integration/test_full_game.py::TestCompleteGameFlow -v
```

**What Integration Tests Validate:**
- Complete game flow from deal to win
- Mahjong rules compliance (turn order, hand sizes, valid melds)
- API response contracts
- Game state consistency
- Concurrent multiplayer isolation
- Win condition detection
- Dealer rotation rules

### Test Options
```bash
# Run with timeout protection
pytest --timeout=60 -v

# Run with coverage report
pytest --cov=mahjong_engine --cov-report=html -v

# Run with verbose debug output
pytest -v --tb=short
```

## How to Run

### Development Server
```bash
# Start the development server (localhost:8080)
python app.py

# Or use the Windows batch file
start_dev.bat
```

The server will start on port 8080 by default. Access the game at `http://localhost:8080`.

### Production Deployment
```bash
# Deploy to Fly.io (requires FLY_API_TOKEN)
fly deploy
```

See `.github/workflows/deploy.yml` for CI/CD configuration.

## Development Workflow (Test-First)

1. **Write test first** - Create failing test in `tests/engine/` or `tests/integration/`
2. **Run test** - `pytest -v path/to/test.py` - Verify it fails (RED)
3. **Write implementation** - Minimal code to pass test in `mahjong_engine/`
4. **Run test again** - `pytest -v path/to/test.py` - Verify it passes (GREEN)
5. **Run all tests** - `pytest -v` - Ensure no regressions
6. **Run linters** - `flake8 && pylint mahjong_engine/` - Check code quality
7. **Run integration tests** - `cd tests/integration && ./run-integration-tests.sh` - Verify gameplay rules
8. **Refactor** - Clean up code while keeping tests green
9. **Commit** - `git add . && git commit -m "description"`

## Code Style Guidelines

### Imports
- Standard library imports first (e.g., `import os`, `import json`)
- Third-party imports second (e.g., `from aiohttp import web`)
- Local/project imports last (e.g., `from mahjong_engine.tile import Tile`)
- Use explicit imports, avoid `import *`
- Group imports with a blank line between each group

Example:
```python
import os
import json
import logging

from aiohttp import web, WSMsgType

from mahjong_engine.tile import Tile
from mahjong_engine.player import Player
```

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
- Always close resources properly (WebSocket connections, files)

Example:
```python
async def websocket_handler(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                # Process message...
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON received: %s", e)
    except Exception as e:
        logger.error("WebSocket error: %s", e)
    finally:
        await ws.close()
```

### Testing Conventions
- Test files: `test_*.py` pattern
- Test classes: `Test*` prefix
- Test functions: `test_*` prefix
- Use pytest markers: `@pytest.mark.integration` for integration tests
- Use descriptive test names explaining what is being tested
- Tests located in `tests/` directory with subdirectories for organization
- Mock external dependencies to keep tests fast and isolated

### Linting Rules

**Flake8** (from `.flake8`):
Following rules are intentionally ignored:
- E501: line too long (handled by 120 char limit instead)
- W291: trailing whitespace
- W293: blank line contains whitespace
- E302: expected 2 blank lines
- E303: too many blank lines
- E231: missing whitespace after ','
- E701: multiple statements on one line

**Pylint** (from `.pylintrc`):
Disabled rules:
- C0111: missing-docstring
- C0103: invalid-name
- R0903: too-few-public-methods
- W0511: fixme
- Line length: 160 (pylint), 120 (flake8/black)
- Max module lines: 2000

## Linting & Formatting

```bash
# Run flake8 linting
flake8

# Run pylint on the engine module
pylint mahjong_engine/

# Format code with black (if installed)
black .

# Sort imports with isort (if installed)
isort .

# Run all quality checks
flake8 && pylint mahjong_engine/
```

## Common Commands

```bash
# Check Python version
python --version

# List installed packages
pip list

# Run Python module directly
python -m mahjong_engine.tile

# Generate requirements.txt (if adding new deps)
pip freeze > requirements.txt

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Check for syntax errors
python -m py_compile app.py
```

## Troubleshooting

### Import Errors
- Ensure you're in the virtual environment: `which python`
- Install dependencies: `pip install -r requirements.txt`
- Check PYTHONPATH includes project root

### Test Failures
- Run single test to isolate: `pytest -k test_name -v`
- Check if integration tests need server running
- Use `--tb=short` for concise tracebacks
- Check pytest cache: `pytest --cache-clear`

### Server Won't Start
- Check port 8080 is not in use: `lsof -i :8080`
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check for syntax errors: `python -m py_compile app.py`

### WebSocket Connection Issues
- Ensure server is running: `python app.py`
- Check browser console for errors
- Verify WebSocket endpoint URL matches environment

## Key Dependencies

- **aiohttp>=3.11.18** - Async web framework and WebSocket support
- **bottle==0.13.3** - Lightweight WSGI micro framework
- **pytest>=8.3.3** - Testing framework
- **pytest-timeout>=2.3.1** - Test timeout protection
- **websockets>=15.0.1** - WebSocket client library

## Notes for AI Agents

### Architecture Understanding
- **mahjong_engine/** is transport-agnostic - it knows nothing about HTTP/WebSocket
- **app.py** handles all web/transport concerns and delegates to the engine
- Game state is managed in memory (single process)
- WebSocket connections manage real-time multiplayer communication

### Testing Strategy
- Unit tests in `tests/engine/` test game logic without server
- Integration tests in `tests/integration/` test full server interactions
- Always run `pytest -m "not integration"` first (faster feedback)
- Integration tests require server to be running

### Critical Considerations
- **Always run tests before committing** - `pytest -v`
- **Run Docker integration tests before merging** - `cd tests/integration && ./run-integration-tests.sh`
- When modifying game logic, ensure engine tests still pass
- WebSocket handlers must properly close connections on errors
- Async/await patterns are used throughout - never block the event loop
- This is deployed to Fly.io - test locally before pushing

### No Existing AI Rules
- No `.cursorrules` file found
- No `.cursor/rules/` directory found
- No `.github/copilot-instructions.md` found

### Design Principles
- **Clean Architecture**: Web layer separated from game logic
- **Interface-Based**: Easy to test and extend
- **Test-First**: Write tests before implementation
- **Async-First**: Use async/await for all I/O operations
- **Single Process**: No distributed complexity, in-memory state

---

**Update this file when you discover new operational knowledge!**
