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

## Monitoring & Observability

### Metrics to Track
- Concurrent games
- WebSocket connection count
- API response times
- Voice recognition accuracy
- Video call quality (bitrate, packet loss)
- Error rates by endpoint

### Tools
- Prometheus + Grafana for metrics
- Sentry for error tracking
- Pino/structlog for structured logging
- Health check endpoints

## Conclusion

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
