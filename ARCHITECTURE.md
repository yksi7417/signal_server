# Signal Server - Architecture Document

## Executive Summary

This document describes the architecture of the Signal Server - a multiplayer Mahjong game platform with video chat and voice control capabilities. The system enables friends to play Mahjong together over the web/mobile, complete with real-time video communication, in-game chat, and voice command controls for game actions.

**Current Status**: Core game engine complete, WebSocket multiplayer functional, basic voice recognition implemented.

**Target Vision**: Full-featured social gaming platform with video chat, persistent chat history, and advanced voice controls.

## Current Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Client (Browser)                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │  Game UI     │ │  Video Chat  │ │  Voice Control   │   │
│  │  (HTML/JS)   │ │  (WebRTC)    │ │  (Web Speech)    │   │
│  └──────┬───────┘ └──────┬───────┘ └────────┬─────────┘   │
└─────────┼────────────────┼──────────────────┼──────────────┘
          │                │                  │
          └────────────────┴──────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Server (aiohttp)                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │  HTTP API    │ │  WebSocket   │ │  Signal Relay    │   │
│  │  Endpoints   │ │  Handler     │ │  (WebRTC)        │   │
│  └──────┬───────┘ └──────┬───────┘ └────────┬─────────┘   │
└─────────┼────────────────┼──────────────────┼──────────────┘
          │                │                  │
          └────────────────┴──────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Game Engine (mahjong_engine)               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │  GameState   │ │  Tile/Meld   │ │  Player/Agent    │   │
│  │  Manager     │ │  Logic       │ │  Controllers     │   │
│  └──────────────┘ └──────────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Game Engine (`mahjong_engine/`)
Transport-agnostic mahjong game logic that can run independently of any web framework.

**Key Classes:**
- `GameState`: Central state manager (dealer rotation, turn management, win detection)
- `Tile`: Represents mahjong tiles with suits, values, and Unicode characters
- `Player`: Player state (hand, revealed sets, score, wind assignment)
- `Meld`: Pung, Kong, Chow, and Pair combinations
- `PlayerAgent`: Abstract agent (Human/AI implementations)
- `RuleSet`: Configurable game rules

**Current Capabilities:**
- 4-player mahjong with AI opponents
- Complete tile set (Dots, Bamboo, Characters, Winds, Dragons, Flowers, Seasons)
- All standard meld types (Pung, Kong, Chow, Pair)
- Win condition validation (standard hand, self-draw)
- Dealer rotation and round wind management

#### 2. Web Server (`app.py`)
Async HTTP/WebSocket server using aiohttp.

**Endpoints:**
- `GET /` - Main game interface
- `GET /voice` - Voice control page
- `GET /voice-command` - WebRTC voice command interface
- `GET /env.js` - Dynamic configuration injection
- `WS /ws` - WebSocket for peer-to-peer signaling

**REST API:**
- `POST /reset-game` - Reset game state
- `POST /start-new-game` - Initialize new game
- `POST /player-claims-pung` - Claim pung (3 of a kind)
- `POST /player-claims-win` - Declare win
- `POST /player-claims-kong` - Claim kong (4 of a kind)
- `POST /advance-dealer` - Advance dealer rotation
- `GET /dealer-info` - Get current dealer/wind info

#### 3. WebSocket Signaling
Peer-to-peer connection management for WebRTC.

**Message Types:**
- `new-peer` - New player joined
- `peer-list` - List of connected peers
- `peer-disconnect` - Player left
- Custom game messages forwarded between peers

#### 4. Voice Control Systems

**A. iPhone Speech Recognition (`SPEECH_RECOGNITION.md`)**
- Browser-based Web Speech API
- Cantonese language support (zh-HK)
- Commands: 食糊, 碰, 開槓, 上, 過
- Tile names: 一筒, 二索, 三萬, 東, 南, etc.

**B. WebRTC Command Server (`webrtc_command_server/`)**
- Server-side voice processing using Whisper
- Local speech-to-text with command parsing
- Planned: GPU-accelerated inference

### Data Flow

```
1. Player opens game in browser
   └── GET / → Returns static/game/index.html
   
2. Browser loads config
   └── GET /env.js → Returns WS_ENDPOINTS for environment
   
3. Player starts call
   └── WS /ws connects → Joins peer network
   
4. Game actions
   ├── Browser → HTTP POST /player-claims-* → Server
   ├── Server → mahjong_engine.GameState → Processes
   └── Server → JSON response → Browser updates UI
   
5. P2P communication (WebRTC)
   ├── Signaling via WebSocket
   └── Direct peer-to-peer for video/audio
```

## Target Architecture

### Vision: Social Multiplayer Mahjong Platform

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Client Applications                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
│  │   Web App   │ │  iOS App    │ │ Android App │ │   Desktop   │  │
│  │  (Browser)  │ │   (Swift)   │ │   (Kotlin)  │  │  (Electron) │  │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘  │
└─────────┼───────────────┼───────────────┼───────────────┼──────────┘
          │               │               │               │
          └───────────────┴───────────────┴───────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      API Gateway (aiohttp/nginx)                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │
│  │  Auth/Rate   │ │   Load       │ │   Static     │                │
│  │  Limiting    │ │   Balancer   │ │   Assets     │                │
│  └──────────────┘ └──────────────┘ └──────────────┘                │
└──────────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   Game Server   │ │   Chat Service   │ │ Presence Service │
│   (aiohttp)     │ │   (WebSocket)    │ │   (Redis)        │
│                 │ │                  │ │                  │
│ ┌─────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────┐ │
│ │ Game Logic  │ │ │ │ Chat Rooms   │ │ │ │ Online Users │ │
│ │ Session Mgmt│ │ │ │ History      │ │ │ │ Game Rooms   │ │
│ └─────────────┘ │ │ └──────────────┘ │ │ └──────────────┘ │
└────────┬────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                   │                    │
         └───────────────────┴────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         Data Layer                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │
│  │  PostgreSQL  │ │    Redis     │ │   S3/MinIO   │                │
│  │  (Game Data) │ │   (Cache)    │ │   (Assets)   │                │
│  └──────────────┘ └──────────────┘ └──────────────┘                │
└──────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      Media Infrastructure                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │
│  │   Janus/     │ │   TURN/      │ │   Whisper    │                │
│  │   Mediasoup  │ │   STUN       │ │   Service    │                │
│  │   (SFU)      │ │   Servers    │ │   (GPU)      │                │
│  └──────────────┘ └──────────────┘ └──────────────┘                │
└──────────────────────────────────────────────────────────────────────┘
```

### Enhanced Features

#### 1. Video Chat Infrastructure

**Current:** P2P WebRTC with basic signaling

**Target:** Selective Forwarding Unit (SFU) for scalability

**Options:**
- **Janus Gateway**: Open-source, proven, good documentation
- **Mediasoup**: Modern, high-performance, Node.js/Rust/C++
- **Pion**: Pure Go, embeddable in aiohttp

**Benefits:**
- Support 4+ players simultaneously
- Better bandwidth management
- Recording capabilities
- Screen sharing

#### 2. Chat System

**Current:** None

**Target:** Persistent chat with history

**Components:**
```python
class ChatService:
    - Room management (game rooms, lobby)
    - Message persistence (PostgreSQL)
    - Real-time delivery (WebSocket)
    - Message types: text, voice note, reaction
```

**Features:**
- In-game chat overlay
- Private messages between friends
- Voice-to-text messages
- Chat history searchable

#### 3. Voice Command Enhancement

**Current:** Browser-based Web Speech API + planned Whisper

**Target:** Full-featured voice control

**Architecture:**
```
Voice Command Flow:
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Audio       │    │  Whisper     │    │  Command     │
│  Capture     │───▶│  STT         │───▶│  Parser      │
│  (Client)    │    │  (GPU)       │    │  (NLP)       │
└──────────────┘    └──────────────┘    └──────────────┘
                                                │
                                                ▼
                                       ┌──────────────┐
                                       │  Game Action │
                                       │  Executor    │
                                       └──────────────┘
```

**Commands:**
- Game: "Pong this tile", "Kong with North wind", "Declare win"
- Chat: "Message John: Good game!"
- Navigation: "Show my hand", "View discard pile"
- Social: "Invite friend", "Start new round"

**Technology:**
- OpenAI Whisper for multilingual STT
- Custom intent classifier for mahjong domain
- Context-aware command resolution

#### 4. User Management & Social

**Current:** Anonymous peer connections

**Target:** Full user system

**Features:**
- User registration/login (OAuth: Google, Apple, WeChat)
- Friend lists and invitations
- Player profiles and statistics
- ELO rating system
- Achievement badges
- Game history and replays

#### 5. Game Room Management

**Current:** Single shared game state

**Target:** Multiple concurrent games

```python
class GameRoomManager:
    - Create/join/leave rooms
    - Spectator mode
    - Private rooms with passwords
    - Public matchmaking
    - Room state persistence (resume interrupted games)
```

### Technology Stack Comparison

| Component | Current | Target | Notes |
|-----------|---------|--------|-------|
| Web Framework | aiohttp | aiohttp + FastAPI | Keep aiohttp for WebSocket, add FastAPI for REST |
| Database | In-memory | PostgreSQL + Redis | Persistent game state, user data |
| Video | P2P WebRTC | SFU (Janus/Mediasoup) | Scalable to 4+ players |
| Chat | None | WebSocket + PostgreSQL | Real-time with history |
| Voice STT | Web Speech API | Whisper + Custom | Better accuracy, more languages |
| Auth | None | JWT + OAuth | Secure user management |
| Deployment | Fly.io | Fly.io + CDN | Global distribution |
| Frontend | Vanilla JS | React/Vue + TS | Better maintainability |

## Implementation Phases

### Phase 1: Foundation (Current)
✅ Core game engine
✅ WebSocket multiplayer
✅ Basic voice recognition
✅ P2P WebRTC signaling

### Phase 2: Enhanced Multiplayer
- [ ] Game room management (create/join/leave)
- [ ] User session management
- [ ] Text chat system
- [ ] Game state persistence

### Phase 3: Social Features
- [ ] User accounts & authentication
- [ ] Friend system
- [ ] Game history & statistics
- [ ] ELO rating

### Phase 4: Video & Voice
- [ ] SFU integration (Janus)
- [ ] 4-player video chat
- [ ] Enhanced voice commands (Whisper)
- [ ] Voice-to-text chat

### Phase 5: Mobile & Polish
- [ ] Mobile app (React Native/Flutter)
- [ ] Push notifications
- [ ] Advanced UI/UX
- [ ] Tournament system

## Key Design Decisions

### 1. Clean Architecture
- Game engine completely separate from web layer
- Can run game logic without HTTP server (testing, AI training)
- Easy to swap transport layers (REST → gRPC, HTTP → WebSocket)

### 2. Async-First
- All I/O operations use async/await
- WebSocket handlers don't block
- Game engine is sync (no I/O), wrapped in async endpoints

### 3. Single Process (Current) → Distributed (Target)
**Current:** Simple, no networking complexity
**Target:** Stateless servers behind load balancer
- Redis for session/game state sharing
- PostgreSQL for persistence
- WebSocket affinity via sticky sessions or pub/sub

### 4. Voice Processing
**Client-side (Web Speech API):**
- Pros: No server cost, low latency
- Cons: Limited language support, browser-dependent

**Server-side (Whisper):**
- Pros: Better accuracy, multilingual, consistent
- Cons: GPU costs, network latency

**Hybrid Approach:**
- Use client-side for quick commands
- Use server-side for complex NLP and chat

## Scalability Considerations

### Current (Single Process)
- Max ~100 concurrent WebSocket connections
- Single game at a time
- Good for: Development, small friend groups

### Target (Distributed)
- Horizontal scaling with load balancer
- Redis for session sharing
- Separate media servers for video
- Good for: Thousands of concurrent games

### Database Schema (Target)

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255),
    oauth_provider VARCHAR(20),
    oauth_id VARCHAR(255),
    created_at TIMESTAMP,
    rating INTEGER DEFAULT 1500
);

-- Game Rooms
CREATE TABLE game_rooms (
    id UUID PRIMARY KEY,
    host_id UUID REFERENCES users(id),
    status VARCHAR(20), -- waiting, playing, finished
    created_at TIMESTAMP,
    config JSONB
);

-- Game Sessions
CREATE TABLE game_sessions (
    id UUID PRIMARY KEY,
    room_id UUID REFERENCES game_rooms(id),
    state JSONB, -- Serialized GameState
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    winner_id UUID REFERENCES users(id)
);

-- Chat Messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    room_id UUID REFERENCES game_rooms(id),
    user_id UUID REFERENCES users(id),
    message TEXT,
    message_type VARCHAR(20), -- text, voice, system
    created_at TIMESTAMP
);

-- Friends
CREATE TABLE friendships (
    user_id UUID REFERENCES users(id),
    friend_id UUID REFERENCES users(id),
    status VARCHAR(20), -- pending, accepted, blocked
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, friend_id)
);
```

## Security Considerations

### Current
- CORS enabled for development
- No authentication
- Open WebSocket connections

### Target
- JWT authentication
- Rate limiting
- Input validation/sanitization
- HTTPS/WSS only
- SQL injection prevention (parameterized queries)
- XSS protection
- CSRF tokens for REST endpoints

## Deployment Architecture

### Development
```
Local Machine
├── Python app.py (aiohttp)
├── Redis (optional)
└── PostgreSQL (optional)
```

### Production
```
Fly.io / AWS / GCP
├── Load Balancer (nginx/traefik)
├── App Servers (3+ instances)
├── Redis Cluster (caching, pub/sub)
├── PostgreSQL (managed)
├── S3/MinIO (assets, recordings)
└── Janus/Media Server (separate VMs)
```

## Integration Testing Strategy

### Pre-Commit Testing Requirements

All code changes must pass the full integration test suite before merging to main. The integration tests validate that the game engine, HTTP API, and WebSocket functionality work together correctly according to mahjong rules.

### Docker-Based Integration Test Environment

#### Test Container Architecture

```
docker-compose.integration.yml
├── signal-server (app container)
│   ├── Exposes port 8080
│   ├── Runs with --reload for development
│   └── Includes test game scenarios
├── test-runner (pytest container)
│   ├── Waits for server health check
│   ├── Executes full game simulation
│   └── Validates game rules compliance
└── test-client (headless browser)
    ├── Simulates 4-player gameplay
    ├── Validates WebSocket connections
    └── Tests voice command integration
```

#### Running Integration Tests Locally

```bash
# Build and start the test environment
docker-compose -f docker-compose.integration.yml up --build

# Run full game simulation test
docker-compose -f docker-compose.integration.yml exec test-runner pytest tests/integration/test_full_game.py -v

# Run with specific scenario
docker-compose -f docker-compose.integration.yml exec test-runner pytest tests/integration/test_scenarios.py::TestWinningScenarios -v

# Cleanup
docker-compose -f docker-compose.integration.yml down -v
```

### Sample Game Simulation Tests

#### Test Scenario 1: Complete 4-Player Game

**Purpose**: Verify a full game from deal to win follows all rules correctly.

```python
# tests/integration/test_full_game.py
class TestCompleteGame:
    """Simulate a complete mahjong game with AI players."""
    
    def test_full_game_flow(self):
        """
        1. Start new game with 4 players
        2. Each player draws and discards tiles
        3. Validate turn order (East -> South -> West -> North)
        4. Verify hand sizes (13 tiles + 1 draw = 14, then discard to 13)
        5. Test pung/kong/chow claims
        6. Validate win condition detection
        7. Confirm dealer rotation on win
        8. Check final scores calculated correctly
        """
        
    def test_wall_exhaustion_flow(self):
        """
        1. Play until wall has < 16 tiles (no more complete rounds)
        2. Verify game ends in draw
        3. Check scores remain unchanged
        4. Validate next round setup
        """
```

#### Test Scenario 2: Rules Compliance Validation

```python
# tests/integration/test_rules_compliance.py
class TestMahjongRules:
    """Validate game follows Hong Kong/Cantonese mahjong rules."""
    
    def test_initial_deal_13_tiles_per_player(self):
        """Each player must start with exactly 13 tiles."""
        
    def test_only_current_player_can_draw(self):
        """Non-current players cannot draw from wall."""
        
    def test_discard_before_claim(self):
        """Claims (pung/kong/win) only valid after tile is discarded."""
        
    def test_winning_hand_requirements(self):
        """
        Winning hand must have:
        - 4 sets (pung/kong/chow) + 1 pair
        - OR special hands (13 orphans, etc.)
        """
        
    def test_pung_priority_over_chow(self):
        """Pung claims have priority over chow claims."""
        
    def test_dealer_rotation_rules(self):
        """
        - Dealer wins: dealer stays, round continues
        - Non-dealer wins: dealer moves to next player
        - 4 rounds complete (East, South, West, North winds)
        """
```

#### Test Scenario 3: API Contract Tests

```python
# tests/integration/test_api_contract.py
class TestAPICompliance:
    """Verify REST API responses match expected contracts."""
    
    def test_start_new_game_response_format(self):
        """
        Response must include:
        - player_hand: list of tile unicode strings
        - game_wind: string (East/South/West/North)
        - current_player_id: integer
        - remaining_tiles: integer
        - dealer_index: integer (0-3)
        """
        
    def test_claim_responses(self):
        """
        All claim endpoints (/player-claims-*) must return:
        - success: boolean
        - message: string
        - action: string (e.g., "discard_after_pung")
        - winner_found: boolean
        - player_hand: list (updated if claim accepted)
        """
        
    def test_websocket_message_types(self):
        """
        WebSocket messages must have:
        - type: string ("new-peer", "peer-list", "peer-disconnect", "game-action")
        - id: string (peer identifier)
        - Additional fields based on type
        """
```

#### Test Scenario 4: Concurrent Multiplayer Tests

```python
# tests/integration/test_concurrent_gameplay.py
class TestConcurrentMultiplayer:
    """Test multiple games running simultaneously."""
    
    def test_four_simultaneous_games(self):
        """
        1. Start 4 separate game sessions
        2. Each with 4 players (16 total connections)
        3. Play concurrent turns
        4. Verify game states remain isolated
        5. No cross-contamination between games
        """
        
    def test_rapid_claim_resolution(self):
        """
        Multiple players claim same discarded tile:
        1. Player A discards tile X
        2. Player B claims pung
        3. Player C claims win
        4. Verify priority: Win > Pung > Kong > Chow
        5. Only highest priority claim succeeds
        """
```

### Integration Test Data Scenarios

#### Scenario Files

Create JSON scenario files for reproducible tests:

```json
// tests/integration/scenarios/winning_hand_scenario.json
{
  "description": "Player 0 should win on 5-dots discard",
  "initial_state": {
    "player_hands": [
      ["一筒", "二筒", "三筒", "四筒", "五筒", "六筒", "七筒", "八筒", "九筒", "東", "東", "南", "南"],
      [/* player 1 hand */],
      [/* player 2 hand */],
      [/* player 3 hand */]
    ],
    "wall": ["五筒", /* remaining tiles */],
    "current_player": 3,
    "game_wind": "East"
  },
  "actions": [
    {"type": "draw", "player": 0},
    {"type": "discard", "player": 0, "tile": "八筒"},
    {"type": "draw", "player": 1},
    {"type": "discard", "player": 1, "tile": "九筒"},
    {"type": "draw", "player": 2},
    {"type": "discard", "player": 2, "tile": "六筒"},
    {"type": "draw", "player": 3},
    {"type": "discard", "player": 3, "tile": "五筒"}
  ],
  "expected_outcome": {
    "winner": 0,
    "winning_tile": "五筒",
    "win_type": "claim_win"
  }
}
```

#### Test Data Loader

```python
# tests/integration/test_scenario_loader.py
class ScenarioLoader:
    """Load and execute game scenarios from JSON files."""
    
    @staticmethod
    def load_scenario(path: str) -> GameScenario:
        """Load scenario and return testable object."""
        
    @staticmethod
    def execute_scenario(scenario: GameScenario) -> TestResult:
        """Run scenario against server and validate outcome."""
```

### CI/CD Integration

#### GitHub Actions Workflow

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  integration-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Start test environment
        run: docker-compose -f docker-compose.integration.yml up -d
      
      - name: Wait for server health
        run: |
          for i in {1..30}; do
            curl -f http://localhost:8080/health && break
            sleep 1
          done
      
      - name: Run game simulation tests
        run: |
          docker-compose -f docker-compose.integration.yml exec -T test-runner \
            pytest tests/integration/test_full_game.py -v --tb=short
      
      - name: Run rules compliance tests
        run: |
          docker-compose -f docker-compose.integration.yml exec -T test-runner \
            pytest tests/integration/test_rules_compliance.py -v
      
      - name: Run API contract tests
        run: |
          docker-compose -f docker-compose.integration.yml exec -T test-runner \
            pytest tests/integration/test_api_contract.py -v
      
      - name: Run concurrent multiplayer tests
        run: |
          docker-compose -f docker-compose.integration.yml exec -T test-runner \
            pytest tests/integration/test_concurrent_gameplay.py -v
      
      - name: Generate test report
        if: always()
        run: |
          docker-compose -f docker-compose.integration.yml exec -T test-runner \
            pytest tests/integration/ --html=report.html --self-contained-html
      
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: integration-test-report
          path: report.html
      
      - name: Cleanup
        if: always()
        run: docker-compose -f docker-compose.integration.yml down -v
```

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running pre-commit integration tests..."

# Build and test
docker-compose -f docker-compose.integration.yml up --build -d

# Wait for ready
sleep 5

# Run tests
if ! docker-compose -f docker-compose.integration.yml exec -T test-runner pytest tests/integration/ -q; then
    echo "❌ Integration tests failed!"
    docker-compose -f docker-compose.integration.yml down -v
    exit 1
fi

echo "✅ Integration tests passed!"
docker-compose -f docker-compose.integration.yml down -v
exit 0
```

### Expected Test Outcomes

All integration tests must demonstrate:

1. **Rule Compliance**:
   - Turn order follows dealer rotation
   - Hand sizes correct at all times
   - Valid melds only (no invalid pung/kong/chow)
   - Win conditions properly validated
   - Scores calculated according to rules

2. **State Consistency**:
   - Game state matches API responses
   - WebSocket broadcasts reflect state changes
   - No race conditions in concurrent access
   - State persists through reconnection (future feature)

3. **API Stability**:
   - Response formats match contracts
   - Error handling returns proper HTTP codes
   - Edge cases handled gracefully (empty wall, invalid claims)

4. **Performance**:
   - API responses < 200ms
   - WebSocket latency < 50ms
   - Concurrent games don't interfere

### Failure Handling

When tests fail:

1. **Capture State**: Save game state snapshot at failure point
2. **Log Replay**: Record all API calls leading to failure
3. **Video Recording**: Capture browser automation replay (if using headless)
4. **Report Generation**: HTML report with failed assertions
5. **Notification**: Slack/Discord notification on CI failure

### Test Maintenance

- Update scenarios when rules change
- Add new scenarios for bug fixes (regression tests)
- Review and update test data quarterly
- Keep Docker images updated (security patches)

## Monitoring & Observability

The Signal Server project has a solid foundation with a clean separation between game logic and web concerns. The current architecture is perfect for development and small-scale deployment.

To achieve the target vision of a social multiplayer platform with video chat and voice control, the recommended path is:

1. **Immediate**: Add game rooms and basic chat
2. **Short-term**: User accounts and persistent sessions
3. **Medium-term**: SFU for video, Whisper for voice
4. **Long-term**: Mobile apps and tournament features

The modular design of the current system makes these enhancements straightforward without major rewrites.

---

**Last Updated**: 2025-02-06
**Version**: 1.0
**Author**: AI Assistant
