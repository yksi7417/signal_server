# Signal Server - Quick Start Guide

Get the Mahjong multiplayer server running in under 5 minutes.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Docker and docker-compose (for integration tests)
- Git

## 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd signal_server

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Run the Server

```bash
# Start the development server
python app.py

# Server will start on http://localhost:8080
```

Open your browser to `http://localhost:8080` to see the game interface.

## 3. Run Tests

### Quick Tests (Unit Tests Only)
```bash
# Fast unit tests - no server required
pytest -m "not integration" -v tests/engine
```

### Full Integration Tests (Requires Docker)
```bash
# Run integration tests in Docker (validates gameplay rules)
cd tests/integration
./run-integration-tests.sh
```

This will:
1. Build test containers
2. Start the server
3. Run complete game simulations
4. Validate mahjong rules compliance
5. Generate test reports

### All Tests
```bash
# Run everything
pytest -v
```

## 4. Development Workflow

### Making Changes

1. **Write a test first** (Test-First Development):
```bash
# Create failing test
# tests/engine/test_your_feature.py
pytest tests/engine/test_your_feature.py -v
```

2. **Implement the feature** to make test pass

3. **Run all tests**:
```bash
pytest -v
```

4. **Run integration tests** (required before commit):
```bash
cd tests/integration && ./run-integration-tests.sh
```

5. **Check code quality**:
```bash
flake8
pylint mahjong_engine/
```

6. **Commit**:
```bash
git add .
git commit -m "Add: brief description of what you did"
```

## 5. Using Ralph Wiggum (Autonomous Development)

This project supports autonomous AI development with Ralph Wiggum.

### Planning Mode
```bash
# Generate or update implementation plan
./loop.sh plan 1
```

### Build Mode
```bash
# Run continuous development loop
./loop.sh build

# Or limit iterations
./loop.sh build 5
```

Ralph will:
1. Read the implementation plan
2. Pick the next task
3. Write tests first
4. Implement the feature
5. Run validation
6. Commit changes
7. Loop again

## 6. Project Structure

```
signal_server/
├── app.py                      # Main web server (aiohttp)
├── mahjong_engine/            # Game logic (no web dependencies)
│   ├── tile.py               # Mahjong tiles
│   ├── player.py             # Player state
│   ├── game_state.py         # Game management
│   ├── hand_validator.py     # Win/meld validation
│   └── ...
├── tests/
│   ├── engine/               # Unit tests (fast)
│   └── integration/          # Integration tests (Docker)
├── static/game/              # Frontend HTML/JS
├── AGENTS.md                 # Operational guide
├── ARCHITECTURE.md           # System architecture
└── IMPLEMENTATION_PLAN.md    # Task tracking
```

## 7. Common Commands

```bash
# Start server
python app.py

# Run unit tests only
pytest -m "not integration" -v tests/engine

# Run specific test
pytest tests/engine/test_tile.py::test_tile_creation -v

# Run integration tests in Docker
cd tests/integration && ./run-integration-tests.sh

# Linting
flake8 && pylint mahjong_engine/

# Check test coverage
pytest --cov=mahjong_engine --cov-report=html

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
```

## 8. Troubleshooting

### Port 8080 already in use
```bash
# Find and kill process
lsof -i :8080
kill -9 <PID>

# Or use different port
APP_PORT=8081 python app.py
```

### Import errors
```bash
# Ensure you're in virtual environment
which python
# Should show: .../venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Integration tests fail
```bash
# Clean up Docker
docker-compose -f tests/integration/docker-compose.integration.yml down -v

# Rebuild and run
cd tests/integration
./run-integration-tests.sh
```

### Tests timeout
```bash
# Run with longer timeout
pytest --timeout=120 -v
```

## 9. Next Steps

1. Read [AGENTS.md](AGENTS.md) for detailed operational guidelines
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
3. Check [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for current tasks
4. Explore `tests/engine/` to understand testing patterns

## 10. Getting Help

- **Documentation**: See AGENTS.md, ARCHITECTURE.md
- **Tests**: Look at `tests/engine/test_*.py` for examples
- **Issues**: Check [GitHub Issues](your-repo-url/issues)

---

**Happy Coding!** 🀄
