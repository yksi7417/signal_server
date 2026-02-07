# Plan: Create AGENTS.md for signal_server

## Objective
Create an AGENTS.md file at `/home/infokey/dvlp/signal_server/AGENTS.md` with build/lint/test commands and code style guidelines.

## Analysis Complete

### Project Type
- Python 3.9+ project
- Uses aiohttp, pytest, flake8, pylint
- Mahjong game server with WebSocket support

### Test Commands Found
- `pytest -v` - Run all tests
- `pytest -m "not integration" -v tests/engine` - Unit tests only
- `pytest -m "integration" -v tests/integration/ -s` - Integration tests only
- `pytest tests/engine/test_tile.py::test_tile_creation -v` - Run specific test
- `pytest -k test_tile_creation -v` - Run by pattern

### Lint Commands Found
- `flake8`
- `pylint mahjong_engine/`

### Code Style Configuration
- Line length: 120 characters
- Indentation: 4 spaces
- Ignored flake8 rules: E501, W291, W293, E302, E303, E231, E701
- Type hints used with Optional[T] and list[T]
- Naming: PascalCase classes, snake_case functions/vars, UPPER_SNAKE_CASE constants

### Project Structure
- app.py - Main aiohttp server
- mahjong_engine/ - Game logic module
- tests/engine/ - Unit tests
- tests/integration/ - Integration tests
- tests/websocket/ - WebSocket tests

### No Existing AI Rules
- No .cursorrules
- No .cursor/rules/
- No .github/copilot-instructions.md

## Action
Write AGENTS.md file with ~150 lines covering all findings.

## Content Preview
The file will include:
1. Project overview
2. All test commands (especially single test execution)
3. Linting/formatting commands
4. Import ordering rules
5. Type hint conventions
6. Naming conventions
7. Error handling patterns
8. Testing conventions
9. Project structure
10. Key dependencies
