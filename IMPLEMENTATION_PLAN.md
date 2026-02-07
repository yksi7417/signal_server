# Implementation Plan

Last updated: 2026-02-06

## Overview

This plan tracks the implementation of the Signal Server - a multiplayer Mahjong game platform with video chat and voice control capabilities.

**Current Status**: Core game engine complete, WebSocket multiplayer functional, integration testing framework in progress.

**Target Vision**: Full-featured social gaming platform with video chat, persistent chat history, user accounts, and advanced voice controls.

---

## Priority 1: Foundation & Testing (Current Focus)

### 1.1 Fix Integration Test Suite
**Status**: In Progress  
**Dependencies**: None  
**Priority**: Critical

- [ ] **Add health check endpoint to app.py**
  - Test: `tests/integration/test_health_endpoint.py`
  - Implementation: Add `GET /health` endpoint to `app.py` that returns `{"status": "ok"}`
  - Validation: `curl http://localhost:8080/health` returns 200 OK
  - File: `app.py:700+` (add new route)

- [ ] **Verify Docker integration test setup**
  - Test: `cd tests/integration && ./run-integration-tests.sh`
  - Validation: Docker containers start successfully, server responds on port 8080
  - Files: `tests/integration/docker-compose.integration.yml`, `tests/integration/run-integration-tests.sh`
  - Fix any path or dependency issues in docker-compose

- [ ] **Create integration test runner script validation**
  - Test: Run `pytest tests/integration/test_full_game.py -v` in Docker
  - Validation: At least one complete game flow test passes
  - Files: `tests/integration/test_full_game.py`, `tests/integration/pytest.ini`

### 1.2 Complete Integration Test Scenarios
**Status**: Not Started  
**Dependencies**: 1.1 Complete  
**Priority**: High

- [ ] **Create scenario loader utility**
  - Test: `tests/integration/test_scenario_loader.py`
  - Implementation: JSON scenario parser in `tests/integration/scenario_loader.py`
  - Validation: Can load and parse `tests/integration/scenarios/*.json` files
  - Format: Follow `ARCHITECTURE.md` section "Integration Test Data Scenarios"

- [ ] **Create winning hand scenario (5-dots claim)**
  - Test: `tests/integration/scenarios/winning_hand_scenario.json`
  - Implementation: JSON scenario file with initial state and expected outcome
  - Validation: Scenario runs through `scenario_loader.py` successfully
  - Reference: See `ARCHITECTURE.md` lines 647-677 for example format

- [ ] **Create pung claim priority scenario**
  - Test: `tests/integration/scenarios/pung_priority_scenario.json`
  - Implementation: Test that pung claims are processed correctly
  - Validation: Scenario validates pung claim flow from discard to reveal

- [ ] **Create wall exhaustion scenario**
  - Test: `tests/integration/scenarios/wall_exhaustion_scenario.json`
  - Implementation: Test game ends correctly when wall is empty
  - Validation: Game state shows `game_ended: true` and proper draw handling

### 1.3 Documentation Completion
**Status**: Partially Complete  
**Dependencies**: None  
**Priority**: Medium

- [ ] **Create QUICKSTART.md for new developers**
  - Test: Have a new developer follow the guide (manual validation)
  - Implementation: Step-by-step setup, build, test, run instructions
  - Validation: Document covers: Python setup, pip install, pytest, docker
  - Include: Prerequisites, installation, running tests, running server

- [ ] **Document WebSocket protocol**
  - Test: `tests/websocket/test_protocol.py` (verify message formats)
  - Implementation: Document all WebSocket message types in `docs/WEBSOCKET_PROTOCOL.md`
  - Validation: Frontend and backend use consistent message formats
  - Reference: `app.py:62-111` for current WebSocket implementation

---

## Priority 2: Core Game Features

### 2.1 Game Mechanics Enhancement
**Status**: Partially Complete  
**Dependencies**: 1.1 Complete  
**Priority**: High

- [ ] **Implement chow (吃) validation in hand_validator.py**
  - Test: `tests/engine/test_melds.py::TestChowValidation`
  - Implementation: Add `can_form_chow(hand, tile)` function to `mahjong_engine/hand_validator.py`
  - Validation: 
    - Chow requires 3 consecutive tiles in same suit (e.g., 1-2-3 of dots)
    - Cannot chow winds or dragons
    - Cannot chow across suits
  - Rules: Only player to left of discarder can claim chow

- [ ] **Add chow claim API endpoint**
  - Test: `tests/integration/test_chow_claim.py`
  - Implementation: Add `POST /api/player_claims_chow` to `app.py`
  - Validation: 
    - Endpoint accepts `confirm_claim` parameter
    - Returns updated hand and revealed sets on success
    - Handles decline flow correctly (advance to next player)
  - Reference: Copy pattern from `player_claims_pung` endpoint

- [ ] **Implement tile discard validation**
  - Test: `tests/engine/test_game_state.py::TestDiscardValidation`
  - Implementation: Validate in `GameState.discard_tile_for_current_player()`
  - Validation:
    - Only current player can discard
    - Tile must exist in player's hand
    - Hand must have 14 tiles (after draw) before discard
  - File: `mahjong_engine/game_state.py` (check existing discard logic)

### 2.2 Game History & Replay
**Status**: Not Started  
**Dependencies**: None  
**Priority**: Medium

- [ ] **Create game history tracker**
  - Test: `tests/engine/test_game_history.py`
  - Implementation: Add `mahjong_engine/game_history.py` with `GameHistory` class
  - Validation:
    - Records all actions: deal, draw, discard, claim, win
    - Stores player hands at each step
    - Can serialize to JSON
  - Format: `[{"action": "draw", "player_id": 0, "tile": "🀇", "timestamp": ...}, ...]`

- [ ] **Add game history API endpoints**
  - Test: `tests/integration/test_game_history_api.py`
  - Implementation: Add to `app.py`:
    - `GET /api/game_history` - Returns current game history
    - `POST /api/save_game` - Saves game history to file
  - Validation: Can retrieve and replay a complete game from history

---

## Priority 3: Multiplayer & Rooms

### 3.1 Game Room Management (Phase 2 Target)
**Status**: Not Started  
**Dependencies**: 1.x Complete, 2.x Complete  
**Priority**: Medium**

- [ ] **Design room data model**
  - Test: `tests/engine/test_room_model.py`
  - Implementation: Create `mahjong_engine/room.py` with `GameRoom` class
  - Validation: Room has unique ID, player list, game state, creation time
  - Attributes: `room_id`, `players[]`, `game_state`, `status`, `created_at`

- [ ] **Implement room creation and joining**
  - Test: `tests/integration/test_game_rooms.py`
  - Implementation: Add to `app.py`:
    - `POST /api/rooms/create` - Create new room
    - `POST /api/rooms/join` - Join existing room
    - `POST /api/rooms/leave` - Leave room
  - Validation: Multiple rooms can exist simultaneously without interference

- [ ] **Add room listing endpoint**
  - Test: `tests/integration/test_room_listing.py`
  - Implementation: `GET /api/rooms/list` returns active rooms
  - Validation: Returns room ID, player count, status for each room

### 3.2 In-Memory Room Store
**Status**: Not Started  
**Dependencies**: 3.1  
**Priority**: Medium**

- [ ] **Create room manager singleton**
  - Test: `tests/engine/test_room_manager.py`
  - Implementation: `mahjong_engine/room_manager.py` with `RoomManager` class
  - Validation:
    - Singleton pattern (one instance across app)
    - Thread-safe operations
    - Automatic cleanup of stale rooms
  - Methods: `create_room()`, `get_room()`, `delete_room()`, `list_rooms()`

---

## Priority 4: Chat & Communication

### 4.1 Text Chat System
**Status**: Not Started  
**Dependencies**: 3.1 (Room system)  
**Priority**: Medium**

- [ ] **Implement WebSocket chat protocol**
  - Test: `tests/integration/test_chat_protocol.py`
  - Implementation: Extend WebSocket handler in `app.py`
  - Message Types:
    - `chat:message` - Text message
    - `chat:history` - Request history
    - `chat:typing` - Typing indicator
  - Validation: Messages broadcast to all players in same room

- [ ] **Add chat persistence (in-memory)**
  - Test: `tests/integration/test_chat_persistence.py`
  - Implementation: Store messages in room object
  - Validation: New joiners receive last 50 messages
  - Format: Store timestamp, sender, message text

---

## Priority 5: Video & Voice

### 5.1 Video Chat SFU Research
**Status**: Not Started  
**Dependencies**: None  
**Priority**: Low**

- [ ] **Evaluate Janus Gateway vs Mediasoup**
  - Test: Proof of concept with both
  - Implementation: Document in `docs/SFU_EVALUATION.md`
  - Criteria:
    - Ease of integration with aiohttp
    - 4+ player support
    - Docker deployment complexity
    - Documentation quality
  - Validation: Decision matrix with scores

### 5.2 Voice Command Enhancement
**Status**: Partially Complete  
**Dependencies**: None  
**Priority**: Low**

- [ ] **Complete WebRTC command server integration**
  - Test: `tests/integration/test_voice_commands.py`
  - Implementation: Integrate Whisper in `webrtc_command_server/`
  - Validation: Voice commands trigger game actions via API
  - Reference: `SPEECH_RECOGNITION.md` for command vocabulary

---

## Priority 6: User Management

### 6.1 Authentication Foundation
**Status**: Not Started  
**Dependencies**: 3.x Complete  
**Priority**: Low**

- [ ] **Design user data model**
  - Test: `tests/engine/test_user_model.py`
  - Implementation: `mahjong_engine/user.py` with `User` class
  - Validation: Supports anonymous and authenticated users
  - Fields: `user_id`, `username`, `created_at`, `stats` (optional)

- [ ] **Implement anonymous session tokens**
  - Test: `tests/integration/test_anonymous_sessions.py`
  - Implementation: JWT tokens for browser sessions
  - Validation: 
    - Token issued on first connection
    - Token persists across reconnects
    - No database required for anonymous users

---

## Completed

- [x] Core mahjong game engine (`mahjong_engine/`)
  - Tile, Player, GameState, Meld classes
  - Hand validation (win detection)
  - AI player agent
  - Dealer rotation system

- [x] WebSocket multiplayer signaling (`app.py`)
  - Peer connection management
  - Message forwarding between peers

- [x] REST API for game actions (`app.py`)
  - Start new game, reset game
  - Draw, discard tiles
  - Pung, Kong, Win claims
  - Dealer rotation endpoints

- [x] Basic voice command recognition
  - iPhone Web Speech API support (`voice.html`)
  - Cantonese language support

- [x] Integration testing framework
  - Docker compose setup
  - pytest configuration
  - Test scripts and scenarios directory

- [x] Documentation
  - `AGENTS.md` - Build/test/run guide
  - `ARCHITECTURE.md` - System design
  - `instruction.md` - Testing framework guidelines

---

## Next Immediate Task

**Task**: Add health check endpoint to app.py  
**Priority**: Critical (blocks integration tests)  
**File**: `app.py`  
**Test**: `tests/integration/test_health_endpoint.py`

**Steps**:
1. Create test file `tests/integration/test_health_endpoint.py`
2. Add `GET /health` route handler to `app.py`
3. Run integration tests to verify
4. Update `docker-compose.integration.yml` healthcheck if needed

---

## Task Dependency Graph

```
Priority 1 (Foundation)
├── 1.1 Health endpoint ← START HERE
├── 1.2 Scenario loader
├── 1.3 Documentation
│
Priority 2 (Core Features)
├── 2.1 Chow validation → requires 1.1
├── 2.2 Game history → requires 1.1
│
Priority 3 (Multiplayer)
├── 3.1 Room model → requires 1.x, 2.x
├── 3.2 Room manager → requires 3.1
│
Priority 4 (Chat)
├── 4.1 Chat system → requires 3.1
│
Priority 5 (Video/Voice)
├── 5.1 SFU evaluation → independent
├── 5.2 Voice commands → requires 5.1
│
Priority 6 (Users)
├── 6.1 User model → requires 3.x
└── 6.2 Sessions → requires 6.1
```

---

## Notes

### Blockers
- Integration tests need health endpoint to verify server readiness
- Docker compose setup needs validation

### Technical Debt
- Global game state in `app.py` needs refactoring for multi-room support
- WebSocket message protocol needs documentation
- Some integration tests are incomplete (chow validation missing)

### Resources Needed
- GPU server for Whisper voice processing (Phase 5)
- PostgreSQL/Redis for production persistence (Phase 3+)
- STUN/TURN servers for WebRTC (Phase 5)

### Development Guidelines
- **Test First**: Write test before implementation
- **One Task Per Loop**: Each task should be completable in one Ralph iteration
- **Run Tests**: Always run `pytest -v` before completing
- **Integration Tests**: Run `cd tests/integration && ./run-integration-tests.sh` for Docker tests

---

**Next Action**: Pick the first unchecked item from Priority 1 and implement it.
