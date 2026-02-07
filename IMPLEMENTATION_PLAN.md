# Implementation Plan

Last updated: 2025-02-06

## Overview

This plan tracks the implementation of the Signal Server - a multiplayer Mahjong game platform with video chat and voice control capabilities.

**Current Status**: Core game engine complete, WebSocket multiplayer functional, integration testing framework in progress.

**Target Vision**: Full-featured social gaming platform with video chat, persistent chat history, user accounts, and advanced voice controls.

---

## Priority 1: Foundation & Testing (Current Focus)

### Testing Infrastructure
- [x] Create comprehensive AGENTS.md with build/test commands
- [x] Document code style guidelines
- [x] Create ARCHITECTURE.md with current and target architecture
- [ ] Fix and verify integration test suite
  - Dependencies: Docker, docker-compose
  - Test: Run `cd tests/integration && ./run-integration-tests.sh`
  - Validation: All integration tests pass
  - Files: `tests/integration/docker-compose.integration.yml`, `tests/integration/test_full_game.py`
- [ ] Complete integration test scenarios
  - Test: `tests/integration/scenarios/*.json`
  - Implementation: Create 5-10 game scenarios covering win conditions, pung/kong/chow claims, wall exhaustion
  - Validation: Scenarios run successfully in Docker
- [ ] Add health check endpoint to app.py
  - Test: `tests/integration/test_health_endpoint.py`
  - Implementation: Add `/health` endpoint to `app.py`
  - Validation: Docker healthcheck passes

### Documentation
- [x] Create Ralph Wiggum loop.sh for Kimi K2.5 Free
- [x] Create PROMPT_build.md for build mode
- [x] Create PROMPT_plan.md for planning mode
- [ ] Create QUICKSTART.md for new developers
  - Dependencies: None
  - Implementation: Document setup, build, test, run steps
  - Validation: New developer can follow guide successfully

---

## Priority 2: Core Game Features

### Game Mechanics
- [ ] Add remaining meld types validation
  - Dependencies: None
  - Test: `tests/engine/test_melds.py::TestChowValidation`, `TestKongValidation`
  - Implementation: Complete chow (吃) and kong (槓) validation in `mahjong_engine/hand_validator.py`
  - Validation: All meld tests pass
- [ ] Implement tile discard validation
  - Dependencies: Current player tracking
  - Test: `tests/engine/test_game_state.py::TestDiscardValidation`
  - Implementation: Validate only current player can discard, tile must be in hand
  - Validation: Integration tests for discard flow
- [ ] Add game history and replay
  - Dependencies: Game state persistence
  - Test: `tests/engine/test_game_history.py`
  - Implementation: Track all actions in `mahjong_engine/game_history.py`
  - Validation: Can replay game from history

### AI Improvements
- [ ] Enhance AI decision making
  - Dependencies: Basic AI working
  - Test: `tests/engine/test_player_agent.py::TestAIDecisions`
  - Implementation: Add strategic tile selection, claim prioritization
  - Validation: AI wins ~25% of games in simulation
- [ ] Add AI difficulty levels
  - Dependencies: Enhanced AI
  - Test: `tests/engine/test_player_agent.py::TestDifficultyLevels`
  - Implementation: Easy/Normal/Hard modes with different strategies
  - Validation: Hard AI beats Easy AI consistently

---

## Priority 3: Multiplayer & Rooms

### Game Room Management
- [ ] Implement game room system
  - Dependencies: None
  - Test: `tests/integration/test_game_rooms.py`
  - Implementation: Room creation, joining, leaving in `app.py`
  - Validation: Multiple concurrent games don't interfere
- [ ] Add room persistence
  - Dependencies: Game room system
  - Test: `tests/integration/test_room_persistence.py`
  - Implementation: Save room state to Redis/PostgreSQL
  - Validation: Can resume interrupted games
- [ ] Implement spectator mode
  - Dependencies: Game room system
  - Test: `tests/integration/test_spectator_mode.py`
  - Implementation: Allow non-players to watch games
  - Validation: Spectators see real-time game updates

### Session Management
- [ ] Add player session handling
  - Dependencies: Game room system
  - Test: `tests/integration/test_sessions.py`
  - Implementation: Session tokens, reconnection logic
  - Validation: Players can reconnect after disconnect
- [ ] Implement game state synchronization
  - Dependencies: Session handling
  - Test: `tests/integration/test_state_sync.py`
  - Implementation: Sync state on reconnect, conflict resolution
  - Validation: No desync issues in 100 game simulation

---

## Priority 4: Chat & Communication

### Text Chat
- [ ] Add in-game chat system
  - Dependencies: Game room system
  - Test: `tests/integration/test_chat.py`
  - Implementation: WebSocket chat in `app.py`, chat history
  - Validation: Messages delivered to all players in room
- [ ] Implement chat persistence
  - Dependencies: Chat system, database
  - Test: `tests/integration/test_chat_history.py`
  - Implementation: Store chat in PostgreSQL
  - Validation: Chat history available after rejoin
- [ ] Add private messaging
  - Dependencies: Chat system
  - Test: `tests/integration/test_private_messages.py`
  - Implementation: Direct messages between players
  - Validation: Only recipient sees private message

### Voice Commands
- [ ] Complete WebRTC command server
  - Dependencies: webrtc_command_server setup
  - Test: `tests/integration/test_voice_commands.py`
  - Implementation: Integrate Whisper STT, command parser
  - Validation: Voice commands trigger game actions
- [ ] Expand voice command vocabulary
  - Dependencies: Basic voice commands
  - Test: `tests/integration/test_voice_vocabulary.py`
  - Implementation: Add English commands, more tile names
  - Validation: 90%+ recognition accuracy in tests

---

## Priority 5: Video & Media

### Video Chat
- [ ] Research and select SFU (Janus vs Mediasoup)
  - Dependencies: None
  - Implementation: Evaluation document, proof of concept
  - Validation: Can run 4-player video call
- [ ] Integrate Janus Gateway
  - Dependencies: SFU selection
  - Test: `tests/integration/test_video_chat.py`
  - Implementation: Docker compose with Janus, signaling integration
  - Validation: 4 players can video chat during game
- [ ] Add screen sharing
  - Dependencies: Video chat working
  - Test: Manual testing
  - Implementation: WebRTC screen capture
  - Validation: Can share screen to other players

---

## Priority 6: User Management

### Authentication
- [ ] Implement user registration/login
  - Dependencies: Database
  - Test: `tests/integration/test_auth.py`
  - Implementation: JWT tokens, password hashing
  - Validation: Can register, login, access protected endpoints
- [ ] Add OAuth providers
  - Dependencies: Auth system
  - Test: `tests/integration/test_oauth.py`
  - Implementation: Google, Apple, WeChat OAuth
  - Validation: Can login with each provider

### Social Features
- [ ] Create friend system
  - Dependencies: User accounts
  - Test: `tests/integration/test_friends.py`
  - Implementation: Friend requests, list, invites
  - Validation: Can add friends, see online status
- [ ] Add player statistics
  - Dependencies: User accounts, game history
  - Test: `tests/integration/test_statistics.py`
  - Implementation: Win/loss tracking, ELO rating
  - Validation: Stats update correctly after games
- [ ] Implement achievement system
  - Dependencies: Statistics
  - Test: `tests/integration/test_achievements.py`
  - Implementation: Achievement definitions, unlocking
  - Validation: Achievements unlock at correct milestones

---

## Priority 7: Mobile & Deployment

### Mobile App
- [ ] Create mobile app prototype
  - Dependencies: API stability
  - Implementation: React Native or Flutter app
  - Validation: Can play game on iOS/Android
- [ ] Add push notifications
  - Dependencies: Mobile app
  - Implementation: FCM/APNs integration
  - Validation: Notifications received when invited to game

### Production Hardening
- [ ] Add rate limiting
  - Dependencies: None
  - Test: `tests/integration/test_rate_limiting.py`
  - Implementation: Redis-based rate limiting
  - Validation: API throttles excessive requests
- [ ] Implement proper logging
  - Dependencies: None
  - Implementation: Structured logging with correlation IDs
  - Validation: Can trace request through logs
- [ ] Add monitoring
  - Dependencies: Deployment
  - Implementation: Prometheus metrics, Grafana dashboards
  - Validation: Dashboards show key metrics

---

## Completed

- [x] Core mahjong game engine
- [x] WebSocket multiplayer signaling
- [x] REST API for game actions
- [x] Voice command recognition (iPhone/Web Speech API)
- [x] Integration testing framework (Docker-based)
- [x] AGENTS.md operational guide
- [x] ARCHITECTURE.md documentation
- [x] Ralph Wiggum loop.sh for autonomous development

---

## Notes

### Current Blockers
- None currently

### Technical Debt
- Some integration tests need completion
- WebRTC command server needs more work
- Need to finalize game room architecture

### Resources Needed
- GPU server for Whisper voice processing
- STUN/TURN servers for WebRTC
- PostgreSQL/Redis for production

---

**Next Task**: Fix and verify integration test suite
