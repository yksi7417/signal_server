# Implementation Plan

Last updated: 2026-02-07

**Status**: Planning Complete - Ready for Implementation  
**Current Phase**: Priority 2 - Core Game Features  
**Next Task**: Task 2.1.1 (Chow validation function)  
**Active Branch**: main

---

## Overview

This plan tracks the implementation of the Signal Server - a multiplayer Mahjong game platform with video chat and voice control capabilities.

**Current State**: 
- Phase 1 Complete: Core game engine, WebSocket multiplayer, integration testing framework
- Phase 2 In Progress: Implementing Chow (吃) claim feature
- Phases 3-5: Planned for future sprints

**Architecture Vision**: Full-featured social gaming platform with video chat, persistent chat history, user accounts, and advanced voice controls.

---

## Priority 1: Foundation & Testing ✅ COMPLETE

### 1.1 Integration Test Infrastructure ✅
**Status**: Complete | **Dependencies**: None

- [x] **Docker integration test environment**
  - Files: `tests/integration/docker-compose.integration.yml`, `tests/integration/run-integration-tests.sh`
  - Validation: `cd tests/integration && ./run-integration-tests.sh`
  - Result: Docker containers start, server responds on port 8080

- [x] **Integration test suite**
  - File: `tests/integration/test_full_game.py`
  - Test Classes: TestCompleteGameFlow, TestRulesCompliance, TestAPIContract
  - Validation: `pytest tests/integration/test_full_game.py -v`

### 1.2 Test Scenarios ✅
**Status**: Complete | **Dependencies**: 1.1

- [x] Winning hand scenario (5-dots claim)
  - File: `tests/integration/scenarios/winning_hand_scenario.json`
- [x] Pung claim priority scenario
  - File: `tests/integration/scenarios/pung_priority_test.json`
- [x] Wall exhaustion scenario
  - File: `tests/integration/scenarios/wall_exhaustion.json`
- [x] Complete game flow scenario
  - File: `tests/integration/scenarios/complete_game_flow.json`

### 1.3 Documentation ✅
**Status**: Complete | **Dependencies**: None

- [x] AGENTS.md - Build/test/run guide
- [x] ARCHITECTURE.md - System design and roadmap
- [x] instruction.md - Testing framework guidelines
- [x] SPEECH_RECOGNITION.md - Voice command integration
- [x] IMPLEMENTATION_PLAN.md - This file

---

## Priority 2: Core Game Features 🔄 IN PROGRESS

### 2.1 Chow (吃) Implementation 🎯 NEXT TASK
**Status**: Ready to implement | **Dependencies**: Priority 1 Complete
**Rationale**: Chow is a fundamental mahjong move that's missing from the current implementation

#### Task 2.1.1: Create chow validation function
**Estimated Time**: 1 iteration
**Test-First**: Yes

**Analysis**: 
- Chow validation logic EXISTS in `_can_form_melds_recursive()` at lines 53-67 of hand_validator.py
- Reference templates: `can_form_pung_with_discard()` (lines 138-155), `can_form_kong_with_discard()` (lines 158-175)
- NO standalone `can_form_chow_with_discard()` function exists

**Implementation Steps**:
1. **Write tests first** (RED phase):
   - Add `TestChowValidation` class to `tests/engine/test_melds.py`
   - Tests: valid chow patterns, position rules, invalid cases
   - Run: `pytest tests/engine/test_melds.py::TestChowValidation -v` (should fail)

2. **Implement function** (GREEN phase):
   - File: `mahjong_engine/hand_validator.py` (after line 188)
   - Signature: `can_form_chow_with_discard(hand, discarded_tile, discarder_position, claimer_position)`
   - Logic:
     - Position check: Only left neighbor can claim `(discarder_position + 1) % 4 == claimer_position`
     - Suit check: Only numeric suits (no winds/dragons): `discarded_tile.is_numeric_suit()`
     - Pattern A (discarded is highest): Need `[N-2, N-1]` in hand
     - Pattern B (discarded is middle): Need `[N-1, N+1]` in hand
     - Pattern C (discarded is lowest): Need `[N+1, N+2]` in hand
   - Run: `pytest tests/engine/test_melds.py::TestChowValidation -v` (should pass)

3. **Validate** (Refactor phase):
   - Run all unit tests: `pytest tests/engine/ -v`
   - Run linting: `flake8 mahjong_engine/hand_validator.py`
   - Run integration tests: `cd tests/integration && ./run-integration-tests.sh`

**Acceptance Criteria**:
- [ ] `TestChowValidation` class exists with 8+ test methods
- [ ] `can_form_chow_with_discard()` implemented with full docstring
- [ ] All chow tests pass
- [ ] No regressions in existing 68 unit tests
- [ ] No flake8/pylint errors

#### Task 2.1.2: Add chow claim API endpoint
**Estimated Time**: 1 iteration
**Dependencies**: Task 2.1.1 Complete
**Test-First**: Yes

**Implementation Steps**:
1. **Write tests**:
   - File: `tests/integration/test_chow_claim.py`
   - Test class: `TestChowClaimAPI`
   - Tests: successful claim, invalid claim, decline flow
   - Run: `pytest tests/integration/test_chow_claim.py -v` (should fail)

2. **Implement endpoint**:
   - File: `app.py` (add after line 699)
   - Pattern: Copy from `player_claims_pung` (lines 184-252)
   - Endpoint: `POST /api/player_claims_chow`
   - Parameters: `confirm_claim` (bool), `tile_to_chow` (string)
   - Logic:
     - Validate chow is legal using `can_form_chow_with_discard()`
     - Update player hand (remove 2 tiles, reveal 3)
     - Advance game state
     - Return updated state
   - Run: `pytest tests/integration/test_chow_claim.py -v` (should pass)

3. **Validate**:
   - Run all integration tests: `pytest tests/integration/ -v`
   - Test via curl: `curl -X POST http://localhost:8080/api/player_claims_chow -H "Content-Type: application/json" -d '{"confirm_claim":true,"tile_to_chow":"1-dot"}'`

**Acceptance Criteria**:
- [ ] `POST /api/player_claims_chow` endpoint responds correctly
- [ ] Endpoint validates chow legality before accepting
- [ ] Updates game state correctly on success
- [ ] Handles decline flow (advances to next player)
- [ ] Integration tests pass

#### Task 2.1.3: Integrate chow into game state logic
**Estimated Time**: 1 iteration
**Dependencies**: Task 2.1.2 Complete
**Test-First**: Yes

**Implementation Steps**:
1. **Write tests**:
   - File: `tests/engine/test_game_state.py`
   - Add to class: `TestChowIntegration`
   - Tests: chow processing, turn validation, state updates
   - Run: `pytest tests/engine/test_game_state.py::TestChowIntegration -v` (should fail)

2. **Implement GameState method**:
   - File: `mahjong_engine/game_state.py`
   - Method: `process_chow_claim(player_id, tile)`
   - Logic:
     - Validate it's the claiming player's turn
     - Remove 2 tiles from hand that form sequence with discarded tile
     - Add 3-tile chow to revealed sets
     - Update current player to claimer
   - Run: `pytest tests/engine/test_game_state.py::TestChowIntegration -v` (should pass)

3. **Validate**:
   - Run full test suite: `pytest -v`
   - Run Docker tests: `cd tests/integration && ./run-integration-tests.sh`

**Acceptance Criteria**:
- [ ] `process_chow_claim()` method exists in GameState
- [ ] Method validates turn order correctly
- [ ] Hand and revealed sets updated correctly
- [ ] Game state advances properly after chow
- [ ] All tests pass

### 2.2 Game History & Replay
**Status**: Not Started | **Dependencies**: None | **Priority**: Medium

#### Task 2.2.1: Create game history tracker class
**Estimated Time**: 1 iteration
**Test-First**: Yes

**Implementation Steps**:
1. **Write tests**:
   - File: `tests/engine/test_game_history.py`
   - Test class: `TestGameHistory`
   - Tests: record actions, serialize to JSON, thread safety
   - Run: `pytest tests/engine/test_game_history.py -v` (should fail)

2. **Implement class**:
   - File: `mahjong_engine/game_history.py` (new file)
   - Class: `GameHistory`
   - Methods:
     - `record_action(action_type, player_id, tile, timestamp)`
     - `get_history()` -> list of action dicts
     - `to_json()` -> JSON string
     - `clear()` -> reset history
   - Format: `[{"action": "draw", "player_id": 0, "tile": "🀇", "timestamp": "..."}, ...]`
   - Run: `pytest tests/engine/test_game_history.py -v` (should pass)

3. **Validate**:
   - Run: `flake8 mahjong_engine/game_history.py`
   - Run: `pylint mahjong_engine/game_history.py`

**Acceptance Criteria**:
- [ ] `GameHistory` class exists with all methods
- [ ] Records all game actions with timestamps
- [ ] JSON serialization works correctly
- [ ] Thread-safe implementation
- [ ] Tests pass

#### Task 2.2.2: Integrate history into GameState
**Estimated Time**: 1 iteration
**Dependencies**: Task 2.2.1 Complete
**Test-First**: Yes

**Implementation Steps**:
1. **Write tests**:
   - File: `tests/engine/test_game_state.py`
   - Add to class: `TestGameHistoryIntegration`
   - Tests: auto-recording, history access, new game clears history
   - Run: `pytest tests/engine/test_game_state.py::TestGameHistoryIntegration -v` (should fail)

2. **Integrate into GameState**:
   - File: `mahjong_engine/game_state.py`
   - Add: `self.history = GameHistory()` in `__init__`
   - Add: History recording calls in `draw_tile()`, `discard_tile()`, `process_pung_claim()`, etc.
   - Add: `get_history()` method that returns `self.history.get_history()`
   - Run: `pytest tests/engine/test_game_state.py::TestGameHistoryIntegration -v` (should pass)

3. **Validate**:
   - Run all tests: `pytest tests/engine/ -v`

**Acceptance Criteria**:
- [ ] GameState has `history` attribute
- [ ] All actions auto-recorded
- [ ] `get_history()` returns complete history
- [ ] History cleared on new game
- [ ] Tests pass

#### Task 2.2.3: Add history API endpoints
**Estimated Time**: 1 iteration
**Dependencies**: Task 2.2.2 Complete
**Test-First**: Yes

**Implementation Steps**:
1. **Write tests**:
   - File: `tests/integration/test_game_history_api.py`
   - Test class: `TestGameHistoryAPI`
   - Tests: retrieve history, save game, load game
   - Run: `pytest tests/integration/test_game_history_api.py -v` (should fail)

2. **Implement endpoints**:
   - File: `app.py`
   - Endpoints:
     - `GET /api/game_history` - Returns JSON history
     - `POST /api/save_game` - Saves history to file
     - `GET /api/saved_games` - Lists saved games
   - Run: `pytest tests/integration/test_game_history_api.py -v` (should pass)

3. **Validate**:
   - Run integration tests: `pytest tests/integration/ -v`

**Acceptance Criteria**:
- [ ] History retrieval endpoint works
- [ ] Save/load game endpoints work
- [ ] JSON format matches schema
- [ ] Integration tests pass

### 2.3 Game Session Management
**Status**: Partial (game_session.py exists) | **Dependencies**: None | **Priority**: Medium

#### Task 2.3.1: Complete GameSession class implementation
**Estimated Time**: 1 iteration
**Test-First**: Yes

**Current State**:
- File: `mahjong_engine/game_session.py` exists (64 lines)
- Current functionality: Global dealer rotation only
- Missing: Session IDs, multi-session support, serialization

**Implementation Steps**:
1. **Write tests**:
   - File: `tests/engine/test_game_session.py`
   - Test class: `TestGameSession`
   - Tests: session creation, unique IDs, serialization, multi-session
   - Run: `pytest tests/engine/test_game_session.py -v` (should fail)

2. **Expand GameSession class**:
   - File: `mahjong_engine/game_session.py`
   - Add to class:
     - `session_id` (UUID)
     - `created_at` (timestamp)
     - `last_activity` (timestamp)
     - `game_state` (GameState instance)
     - `to_dict()` -> serialize to dict
     - `from_dict(data)` -> deserialize from dict
     - `update_activity()` -> update last_activity timestamp
   - Run: `pytest tests/engine/test_game_session.py -v` (should pass)

3. **Validate**:
   - Run: `flake8 mahjong_engine/game_session.py`
   - Run all engine tests: `pytest tests/engine/ -v`

**Acceptance Criteria**:
- [ ] GameSession has unique UUID
- [ ] Tracks creation and last activity times
- [ ] Can serialize/deserialize game state
- [ ] Supports multiple concurrent sessions
- [ ] Tests pass

#### Task 2.3.2: Add session management API
**Estimated Time**: 1 iteration
**Dependencies**: Task 2.3.1 Complete
**Test-First**: Yes

**Implementation Steps**:
1. **Write tests**:
   - File: `tests/integration/test_session_api.py`
   - Test class: `TestSessionAPI`
   - Tests: create session, join session, get session state, multi-session isolation
   - Run: `pytest tests/integration/test_session_api.py -v` (should fail)

2. **Implement endpoints**:
   - File: `app.py`
   - Endpoints:
     - `POST /api/sessions/create` - Create new session, returns session_id
     - `GET /api/sessions/{session_id}` - Get session state
     - `POST /api/sessions/{session_id}/join` - Join existing session
     - `POST /api/sessions/{session_id}/leave` - Leave session
   - Add: Session manager (dict mapping session_id -> GameSession)
   - Run: `pytest tests/integration/test_session_api.py -v` (should pass)

3. **Validate**:
   - Run integration tests: `pytest tests/integration/ -v`
   - Run Docker tests: `cd tests/integration && ./run-integration-tests.sh`

**Acceptance Criteria**:
- [ ] Multiple sessions can exist simultaneously
- [ ] Sessions are isolated (no cross-contamination)
- [ ] Players can join/leave sessions
- [ ] Session cleanup after inactivity (optional)
- [ ] Integration tests pass

---

## Priority 3: Multiplayer & Rooms ⏳ PLANNED

### 3.1 Game Room Management
**Status**: Not Started | **Dependencies**: Priority 2 Complete | **Priority**: Medium

#### Task 3.1.1: Design and implement room data model
**Estimated Time**: 1 iteration
**Test-First**: Yes

**Implementation**:
- File: `mahjong_engine/room.py` (new file)
- Class: `GameRoom`
- Attributes: `room_id` (UUID), `players[]`, `game_state`, `status`, `created_at`, `max_players`
- Test: `tests/engine/test_room_model.py`
- Validation: `pytest tests/engine/test_room_model.py -v`

#### Task 3.1.2: Implement room manager singleton
**Estimated Time**: 1 iteration
**Dependencies**: Task 3.1.1 Complete
**Test-First**: Yes

**Implementation**:
- File: `mahjong_engine/room_manager.py` (new file)
- Class: `RoomManager` (singleton)
- Methods: `create_room()`, `get_room()`, `delete_room()`, `list_rooms()`, `cleanup_stale()`
- Features: Thread-safe, auto-cleanup after 24h inactivity
- Test: `tests/engine/test_room_manager.py`
- Validation: `pytest tests/engine/test_room_manager.py -v`

#### Task 3.1.3: Create room management API endpoints
**Estimated Time**: 1 iteration
**Dependencies**: Task 3.1.2 Complete
**Test-First**: Yes

**Implementation**:
- File: `app.py`
- Endpoints:
  - `POST /api/rooms/create`
  - `POST /api/rooms/{room_id}/join`
  - `POST /api/rooms/{room_id}/leave`
  - `GET /api/rooms/list`
  - `GET /api/rooms/{room_id}`
- Test: `tests/integration/test_game_rooms.py`
- Validation: `pytest tests/integration/test_game_rooms.py -v`

#### Task 3.1.4: Add room-based WebSocket messaging
**Estimated Time**: 1 iteration
**Dependencies**: Task 3.1.3 Complete
**Test-First**: Yes

**Implementation**:
- File: `app.py` (extend `websocket_handler`)
- Features:
  - Room ID tracked per WebSocket connection
  - Messages broadcast only to same room
  - Cleanup on disconnect
- Test: `tests/websocket/test_room_messaging.py`
- Validation: `pytest tests/websocket/test_room_messaging.py -v`

---

## Priority 4: Chat & Communication ⏳ PLANNED

### 4.1 Text Chat System
**Status**: Not Started | **Dependencies**: Priority 3 Complete | **Priority**: Medium

#### Task 4.1.1: Implement chat message data model
**Estimated Time**: 1 iteration
**Dependencies**: Task 3.1 Complete
**Test-First**: Yes

**Implementation**:
- File: `mahjong_engine/chat.py` (new file)
- Class: `ChatMessage`
- Format: `{"timestamp": "ISO8601", "sender_id": "uuid", "content": "text", "type": "text|system"}`
- Test: `tests/engine/test_chat_message.py`
- Validation: `pytest tests/engine/test_chat_message.py -v`

#### Task 4.1.2: Implement in-memory chat persistence
**Estimated Time**: 1 iteration
**Dependencies**: Task 4.1.1 Complete
**Test-First**: Yes

**Implementation**:
- File: `mahjong_engine/room.py` (add to Room class)
- Features:
  - Store last 100 messages (circular buffer)
  - New joiners receive message history
- Test: `tests/engine/test_chat_persistence.py`
- Validation: `pytest tests/engine/test_chat_persistence.py -v`

#### Task 4.1.3: Implement WebSocket chat protocol
**Estimated Time**: 1 iteration
**Dependencies**: Task 4.1.2 Complete
**Test-First**: Yes

**Implementation**:
- File: `app.py` (extend WebSocket handler)
- Message Types:
  - `chat:message` - Text message
  - `chat:history` - Request history
  - `chat:typing` - Typing indicator
  - `chat:system` - System messages
- Test: `tests/integration/test_chat_protocol.py`
- Validation: `pytest tests/integration/test_chat_protocol.py -v`

---

## Priority 5: Video & Voice ⏳ PLANNED

### 5.1 Video Chat SFU Research
**Status**: Not Started | **Dependencies**: None | **Priority**: Low

#### Task 5.1.1: Evaluate SFU options
**Estimated Time**: 1 iteration (research only)
**Deliverable**: Decision document

**Research**:
- Options: Janus Gateway, Mediasoup, Pion
- Criteria: Integration ease, 4+ player support, Docker deployment, documentation
- File: `docs/SFU_EVALUATION.md` (new file)
- Output: Decision matrix with recommendation

### 5.2 Voice Command Enhancement
**Status**: Partial (webrtc_command_server/ exists) | **Dependencies**: None | **Priority**: Low

#### Task 5.2.1: Complete WebRTC command server integration
**Estimated Time**: 2 iterations
**Dependencies**: None
**Test-First**: Yes

**Current State**: `webrtc_command_server/` directory exists with basic structure

**Implementation**:
- Directory: `webrtc_command_server/`
- Components:
  - Audio capture from browser
  - Whisper STT processing
  - Command parsing
  - API integration for game actions
- Test: `tests/integration/test_voice_commands.py`
- Validation: `pytest tests/integration/test_voice_commands.py -v`

---

## Priority 6: User Management ⏳ PLANNED

### 6.1 Authentication Foundation
**Status**: Not Started | **Dependencies**: Priority 3 Complete | **Priority**: Low

#### Task 6.1.1: Design user data model
**Estimated Time**: 1 iteration
**Dependencies**: Task 3.x Complete
**Test-First**: Yes

**Implementation**:
- File: `mahjong_engine/user.py` (new file)
- Class: `User`
- Fields: `user_id` (UUID), `username`, `display_name`, `created_at`, `stats` (optional)
- Supports: Anonymous and authenticated users
- Test: `tests/engine/test_user_model.py`
- Validation: `pytest tests/engine/test_user_model.py -v`

#### Task 6.1.2: Implement anonymous session tokens
**Estimated Time**: 1 iteration
**Dependencies**: Task 6.1.1 Complete
**Test-First**: Yes

**Implementation**:
- File: `app.py` (middleware)
- Technology: JWT tokens
- Features:
  - Token issued on first connection
  - Persists across reconnects
  - No database for anonymous users
  - Token includes user_id and room_id
- Test: `tests/integration/test_anonymous_sessions.py`
- Validation: `pytest tests/integration/test_anonymous_sessions.py -v`

---

## Completed Tasks Archive

### Foundation (Phase 1)
- [x] Core mahjong game engine (`mahjong_engine/`)
  - Tile, Player, GameState, Meld classes
  - Hand validation (win detection)
  - AI player agent
  - Dealer rotation system
  - Tile factory and Unicode support
- [x] WebSocket multiplayer signaling (`app.py`)
- [x] REST API for game actions (`app.py`)
- [x] Docker integration testing framework
- [x] Integration test scenarios

### Voice Recognition
- [x] Basic voice command recognition (`voice.html`)
- [x] Cantonese language support (zh-HK)
- [x] Commands: 食糊, 碰, 開槓, 上, 過

---

## Task Dependency Graph

```
Priority 1 (Foundation) ✅ COMPLETE
├── 1.1 Docker tests ✅
├── 1.2 Scenarios ✅
└── 1.3 Documentation ✅

Priority 2 (Core Features) 🔄 START HERE
├── 2.1 Chow validation ← NEXT TASK (2.1.1)
│   ├── 2.1.1 can_form_chow_with_discard() ← IMPLEMENT THIS
│   ├── 2.1.2 API endpoint (depends on 2.1.1)
│   └── 2.1.3 GameState integration (depends on 2.1.2)
├── 2.2 Game history (independent)
│   ├── 2.2.1 GameHistory class
│   ├── 2.2.2 GameState integration (depends on 2.2.1)
│   └── 2.2.3 API endpoints (depends on 2.2.2)
└── 2.3 Game sessions (independent)
    ├── 2.3.1 Complete GameSession class
    └── 2.3.2 Session API (depends on 2.3.1)

Priority 3 (Rooms) ⏳
├── 3.1 Room management (depends on 2.x)
│   ├── 3.1.1 Room model
│   ├── 3.1.2 Room manager (depends on 3.1.1)
│   ├── 3.1.3 Room API (depends on 3.1.2)
│   └── 3.1.4 WebSocket rooms (depends on 3.1.3)

Priority 4 (Chat) ⏳
├── 4.1 Chat system (depends on 3.1)
│   ├── 4.1.1 Chat message model
│   ├── 4.1.2 In-memory persistence (depends on 4.1.1)
│   └── 4.1.3 WebSocket protocol (depends on 4.1.2)

Priority 5 (Video/Voice) ⏳
├── 5.1 SFU evaluation (independent)
└── 5.2 Voice commands (depends on 5.1)

Priority 6 (Users) ⏳
├── 6.1 User model (depends on 3.x)
└── 6.2 Anonymous sessions (depends on 6.1)
```

---

## Development Guidelines

### Test-First Development Workflow
1. Write failing test before implementation
2. Run test to confirm it fails (RED)
3. Write minimal code to pass test (GREEN)
4. Refactor while keeping tests passing
5. Run full test suite before completing

### Task Completion Checklist
- [ ] Test file created with failing tests
- [ ] Implementation code written
- [ ] Tests pass: `pytest path/to/test.py -v`
- [ ] No regressions: `pytest -v`
- [ ] Linting passes: `flake8 && pylint mahjong_engine/`
- [ ] Docker tests pass: `cd tests/integration && ./run-integration-tests.sh`
- [ ] Documentation updated if needed

### Code Style Requirements
- 4 spaces indentation (no tabs)
- Line length: 120 characters
- Type hints for function parameters
- Docstrings for all public functions
- Follow AGENTS.md conventions

### Commit Message Format
```
feat: Add chow validation for mahjong claims

- Implement can_form_chow_with_discard() in hand_validator.py
- Support consecutive tile sequences (1-2-3, 4-5-6, etc.)
- Validate position rule (only left neighbor can claim)
- Exclude winds and dragons from chow validation
- Add comprehensive unit tests in TestChowValidation

Closes #2.1.1
```

---

## Quick Reference

### Test Commands
```bash
# Run unit tests only (fast)
pytest -m "not integration" -v tests/engine

# Run specific test
pytest tests/engine/test_melds.py::TestChowValidation -v

# Run all tests
pytest -v

# Run Docker integration tests
cd tests/integration && ./run-integration-tests.sh

# Run with coverage
pytest --cov=mahjong_engine --cov-report=html -v
```

### Code Quality Commands
```bash
flake8 mahjong_engine/
pylint mahjong_engine/
black mahjong_engine/  # if installed
```

### Key Files for Current Task (2.1.1)
- **Test**: `tests/engine/test_melds.py` (add TestChowValidation class)
- **Implementation**: `mahjong_engine/hand_validator.py` (add after line 188)
- **Reference**: `can_form_pung_with_discard()` at lines 138-155

---

## Current Status Summary

**Test Count**:
- Unit tests: 50+ passing (tests/engine/)
- Integration tests: 34+ passing (tests/integration/)

**Next Action**: Implement Task 2.1.1 - Create `can_form_chow_with_discard()` function in `mahjong_engine/hand_validator.py`

**Blockers**: None

**Ready to Start**: Task 2.1.1

---

**Last Updated**: 2026-02-07
**Version**: 2.0
**Status**: Planning Complete
