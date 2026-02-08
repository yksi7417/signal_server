# SFU Evaluation for Signal Server

**Date:** 2026-02-08
**Task:** 5.1.1 - Evaluate SFU options
**Status:** Complete
**Author:** AI Assistant

---

## Executive Summary

This document evaluates Selective Forwarding Unit (SFU) options for adding video chat to the Signal Server mahjong platform. Our use case is **4-player video chat** during mahjong games, with a Python/aiohttp backend deployed via Fly.io.

**Recommendation:** **LiveKit** (built on Pion/Go) as a separate microservice, with the existing Python/aiohttp server handling game logic and signaling orchestration.

**Runner-up:** Janus Gateway, if more protocol flexibility is needed (SIP, RTSP, etc.).

---

## Use Case Requirements

| Requirement | Detail |
|---|---|
| **Participants per room** | 4 (fixed for mahjong) |
| **Media types** | Video + Audio |
| **Backend language** | Python 3.9+ (aiohttp) |
| **Deployment** | Fly.io (Docker containers) |
| **Scale** | Small (1-50 concurrent rooms initially) |
| **Video quality** | 360p-480p sufficient (face visibility, not fine detail) |
| **Additional features** | Mute/unmute, spectator mode (future), screen share (future) |
| **Budget** | Open-source preferred, minimal infrastructure cost |

---

## Options Evaluated

1. **Janus Gateway** - C-based plugin architecture
2. **Mediasoup** - C++/Node.js library approach
3. **Pion/LiveKit** - Go-based WebRTC framework/server
4. **aiortc** - Pure Python WebRTC (bonus evaluation)

---

## 1. Janus Gateway

### Overview

| Attribute | Value |
|---|---|
| **Language** | C |
| **License** | GPLv3 (commercial license available) |
| **GitHub Stars** | ~8,800 |
| **Latest Version** | v1.3.1 (March 2025) |
| **First Released** | 2014 |
| **Maintainer** | Meetecho (Italian company) |

### Architecture

Janus is a **modular, plugin-based gateway**. The core handles WebRTC transport (ICE, DTLS, SRTP) while plugins provide application logic:

- **VideoRoom** - Multi-party SFU (our primary interest)
- **AudioBridge** - Server-mixed audio conferencing (MCU)
- **TextRoom** - Data channel text chat
- **Streaming** - One-to-many broadcasting
- **SIP/NoSIP** - SIP gateway
- **Record&Play** - Session recording
- **EchoTest** - Diagnostic tool
- **Lua/Duktape** - Custom scripting plugins

Supports simulcast (VP8/H.264) and SVC (VP9/AV1) for adaptive quality.

### Python Integration

Janus runs as a **separate process**, communicating via HTTP/WebSocket JSON API. Our Python server would relay signaling (SDP/ICE) between browsers and Janus. Media flows directly between browsers and Janus.

```
Browser <--WebSocket--> Python/aiohttp <--HTTP/WS--> Janus Gateway
Browser <--WebRTC (media)--> Janus Gateway (direct)
```

Available Python libraries: `janus-client` (PyPI), `aiortc` examples.

### 4-Player Performance

Trivial workload. With multistream: 8 PeerConnections total. Janus handles 150+ publishers on a single server. A 4-player room uses <5% of a single CPU core.

### Docker Deployment

No official Docker image; community images available (`canyan/janus-gateway`). Requires UDP port range mapping and `nat_1_1_mapping` configuration for public IP. Moderate complexity.

### Pros

- Battle-tested maturity (10+ years)
- VideoRoom plugin maps directly to our use case
- Built-in TextRoom could supplement WebSocket chat
- AudioBridge available for mixed audio (lower bandwidth)
- Rich plugin ecosystem for future expansion (SIP, recording)
- Separate service model keeps GPL isolated from our Python code

### Cons

- **GPLv3 license** - Copyleft concerns for some organizations
- Steep learning curve (session/handle/plugin model)
- C codebase for debugging/custom plugins
- No official Docker image
- JavaScript-first client ecosystem
- Requires separate TURN server (e.g., coturn)

---

## 2. Mediasoup

### Overview

| Attribute | Value |
|---|---|
| **Language** | C++ (media worker) + Node.js/Rust (control) |
| **License** | ISC (permissive, MIT-equivalent) |
| **GitHub Stars** | ~7,100 |
| **Latest Version** | 3.19.17 (February 2026) |
| **First Released** | ~2015 |
| **Maintainer** | Versatica (Inaki Baz Castillo) |

### Architecture

Mediasoup is a **library, not a standalone server**. It uses a two-layer architecture:

1. **Control plane** (Node.js or Rust): Application API for orchestrating media sessions
2. **Media plane** (C++ subprocesses): CPU-intensive packet forwarding via libuv

Object hierarchy: Worker -> Router -> Transport -> Producer/Consumer

One Worker per CPU core. A Worker handles ~500 consumers. Signaling is completely application-defined.

### Python Integration

**No native Python server support.** The mediasoup server component runs only in Node.js or Rust. Integration requires running a Node.js (or Rust) sidecar:

- Python handles game logic + signaling
- Node.js/Rust handles mediasoup Workers
- Communication via Redis, RabbitMQ, HTTP, or Unix sockets

`pymediasoup` (v1.2.1) exists but is a **client-side library** (uses aiortc), not a server replacement.

### 4-Player Performance

24 total consumers per room (4 players x 6 consumers each). A single CPU core handles ~500 consumers, so one core supports ~20 simultaneous 4-player rooms. Excellent performance-to-resource ratio.

### Docker Deployment

Achievable with community images. Same networking challenges as all WebRTC servers: announced IP configuration, UDP port ranges. Building the C++ worker requires build tools in the container.

### Pros

- ISC license (fully permissive, no commercial restrictions)
- Best-in-class raw performance (~500 consumers/core)
- Rust crate available (avoids Node.js dependency)
- Signaling agnostic (full control over protocol)
- Fine-grained media routing control
- Active maintenance (15 open issues is remarkably low)

### Cons

- **No Python server support** - Requires Node.js or Rust sidecar
- **Two-service architecture** adds operational complexity
- Steep learning curve (low-level library, not framework)
- No built-in signaling (more code to write)
- No built-in recording
- Small Python ecosystem (`pymediasoup` has only 32 GitHub stars)

---

## 3. Pion / LiveKit

### Overview

**Pion** is a pure Go WebRTC library (framework). **LiveKit** is a production-grade SFU server built on Pion.

| Attribute | Pion | LiveKit |
|---|---|---|
| **Language** | Go | Go (built on Pion) |
| **License** | MIT | Apache-2.0 |
| **GitHub Stars** | ~16,000 | ~22,000 |
| **Latest Version** | v4.2.0 (Dec 2025) | Active releases |
| **Type** | Library | Complete SFU server |
| **Maintainer** | Community (nonprofit) | LiveKit Inc. (commercial) |

### Architecture (LiveKit)

LiveKit provides a **complete, batteries-included SFU**:

- Room management with participant tracking
- Adaptive bitrate with simulcast
- Built-in TURN server
- JWT-based authentication
- Webhook notifications
- Server-side APIs for room control
- SDKs for 11+ platforms including **Python**

```
Browser <--WebSocket--> Python/aiohttp (game logic, tokens)
Browser <--WebRTC--> LiveKit Server (media)
Python/aiohttp <--REST API--> LiveKit Server (room management)
LiveKit Server <--Webhooks--> Python/aiohttp (events)
```

### Python Integration

**Official Python SDK** (`livekit` package) provides:
- Room management (create, list, delete rooms)
- Token generation (JWT access tokens for clients)
- Participant control (mute, kick, permissions)
- Webhook parsing (participant joined/left, track events)

This is the **cleanest Python integration** of all options evaluated.

### 4-Player Performance

Trivially small workload. LiveKit is designed for rooms with dozens of participants. A single-core VPS handles multiple 4-player rooms easily. ~50-100 MB memory for 4 participants.

### Docker Deployment

**Official Docker images** available. Development mode: `livekit-server --dev`. Production: well-documented Docker Compose and Kubernetes deployment guides. Port requirements: 7880 (HTTP), 7881 (gRPC), 7882 (UDP media).

### Pros

- **Official Python SDK** - Best integration story for our stack
- **Complete solution** - Room management, auth, TURN, simulcast all built in
- **Excellent documentation** - Comprehensive docs, tutorials, examples
- **Large community** - 22k stars, professionally maintained
- **Easy Docker deployment** - Official images, `--dev` mode for development
- **Permissive license** - Apache-2.0
- **Single binary** - Go compiles to one static binary, minimal container footprint
- **Built-in TURN** - No separate coturn needed

### Cons

- Separate Go service alongside Python (adds operational complexity)
- May be overkill for a fixed 4-player scenario
- Backed by a commercial company (risk of future licensing changes, though Apache-2.0 is irrevocable)
- WebRTC NAT traversal still requires careful network configuration

---

## 4. aiortc (Python-Native Alternative)

### Overview

| Attribute | Value |
|---|---|
| **Language** | Python (pure, asyncio-based) |
| **License** | BSD-3-Clause |
| **GitHub Stars** | ~5,000 |
| **Maintainer** | Jeremy Laine |
| **Codecs** | Opus, PCMU/PCMA (audio); VP8, H.264 (video) |

### Could We Build an SFU with aiortc?

**Technically possible, practically risky.** aiortc can create server-side PeerConnections and forward media between them. However:

- **No production SFU exists built on aiortc** - This is telling
- Reported CPU/memory issues with multiple concurrent connections
- Python GIL limits parallel packet processing
- No SFU primitives (simulcast selection, bandwidth estimation, adaptive forwarding)
- Reported fragility with rapid connections/disconnections
- Author positions it for "education and innovation," not production media servers

### Pros

- **Same process** - No separate service, runs in aiohttp event loop
- **Python native** - Single language stack
- **Simple for prototyping** - Quick to get working for 4 players

### Cons

- **Unproven as SFU** - No production examples exist
- **Performance risk** - CPU/memory concerns with multiple connections
- **Missing features** - No simulcast, no ABR, no bandwidth estimation
- **Technical debt** - Building SFU from scratch creates maintenance burden
- **Not recommended** for production use

---

## Decision Matrix

| Criterion (Weight) | Janus | Mediasoup | LiveKit | aiortc |
|---|---|---|---|---|
| **Python Integration (25%)** | 6/10 | 4/10 | **9/10** | 8/10 |
| **4+ Player Support (15%)** | 10/10 | 10/10 | **10/10** | 6/10 |
| **Docker Deployment (15%)** | 6/10 | 6/10 | **9/10** | 7/10 |
| **Documentation (15%)** | 7/10 | 7/10 | **9/10** | 5/10 |
| **Community & Maturity (10%)** | 9/10 | 8/10 | **9/10** | 6/10 |
| **License (10%)** | 5/10 | **10/10** | **9/10** | 9/10 |
| **Operational Simplicity (10%)** | 5/10 | 4/10 | 7/10 | **9/10** |
| **Weighted Score** | **6.55** | **6.30** | **8.75** | **6.85** |

---

## Recommendation

### Primary: LiveKit (Pion-based)

**LiveKit** is the recommended SFU for the Signal Server project:

1. **Best Python integration** - Official SDK with room management, token generation, and webhooks
2. **Complete solution** - No need to build signaling, room management, or auth from scratch
3. **Easiest deployment** - Official Docker images, `--dev` mode, built-in TURN
4. **Best documentation** - Comprehensive guides for our exact use case
5. **Permissive license** - Apache-2.0, no commercial restrictions
6. **Future-proof** - Scales well beyond 4 players if we add spectator mode or larger rooms

### Architecture

```
                    +-----------------+
                    |   Browser (4x)  |
                    |  Game UI + Video|
                    +---+--------+----+
                        |        |
               WebSocket|        |WebRTC (media)
                        |        |
                   +----+----+   |
                   | Python  |   |
                   | aiohttp |   |
                   | Server  |   |
                   |         |   |
                   | - Game  |   |
                   | - Chat  |   |
                   | - Rooms |   |
                   | - Auth  |   |
                   +----+----+   |
                        |        |
                   REST |        |
                   API  |        |
                        |        |
                   +----+--------+----+
                   |   LiveKit Server |
                   |   (Go/Pion SFU)  |
                   |                  |
                   |  - Video routing |
                   |  - Simulcast     |
                   |  - TURN          |
                   +------------------+
```

### Implementation Steps (Next Tasks)

1. **Task 5.1.2**: Set up LiveKit development environment
   - Install LiveKit server locally (`livekit-server --dev`)
   - Install Python SDK (`pip install livekit`)
   - Create proof-of-concept: 4 browsers joining a video room

2. **Task 5.1.3**: Integrate LiveKit with Signal Server
   - Add LiveKit token generation to Python server
   - Add room lifecycle management (create on game start, destroy on game end)
   - Add LiveKit webhooks for participant events
   - Update frontend to connect to LiveKit for video

3. **Task 5.1.4**: Docker deployment
   - Add LiveKit to `docker-compose.yml`
   - Configure networking (UDP ports, public IP)
   - Test in Docker environment

### Fallback: Janus Gateway

If LiveKit proves unsuitable (e.g., Fly.io networking issues, need for SIP integration, or desire for more protocol flexibility), **Janus Gateway** is the recommended fallback. Its VideoRoom plugin maps directly to our use case, and its plugin ecosystem offers features (SIP, recording, text rooms) that LiveKit doesn't.

---

## Resource Estimates (4-Player Room at 480p)

| Resource | Per Room | 10 Concurrent Rooms |
|---|---|---|
| **CPU** | ~0.5% of 1 core | ~5% of 1 core |
| **Memory** | ~50 MB | ~200 MB |
| **Bandwidth (server)** | ~16 Mbps | ~160 Mbps |
| **Client upload** | ~1 Mbps per player | - |
| **Client download** | ~3 Mbps per player | - |

**Minimum server spec:** 1 vCPU, 1 GB RAM, 100 Mbps bandwidth (handles ~6 concurrent rooms at 480p, limited by bandwidth).

**Recommended for production:** 2 vCPU, 2 GB RAM, 1 Gbps bandwidth.

---

## WebRTC Video Bitrate Reference

| Resolution | Bitrate (video + audio) |
|---|---|
| 240p @ 30fps | ~500 Kbps |
| 360p @ 30fps | ~600-800 Kbps |
| 480p @ 30fps | ~1.0-1.5 Mbps |
| 720p @ 30fps | ~1.5-2.5 Mbps |
| 1080p @ 30fps | ~3.0-5.0 Mbps |

**Recommendation for mahjong:** 360p-480p is optimal. Players need face visibility, not fine detail. This keeps bandwidth manageable for mobile players.

---

## Sources

### Janus Gateway
- [Janus WebRTC Server - Official Site](https://janus.conf.meetecho.com/)
- [meetecho/janus-gateway - GitHub](https://github.com/meetecho/janus-gateway)
- [VideoRoom Plugin Documentation](https://janus.conf.meetecho.com/docs/videoroom.html)
- [Janus Plugins List](https://janus.conf.meetecho.com/docs/pluginslist.html)
- [Janus FAQ](https://janus.conf.meetecho.com/docs/FAQ.html)
- [janus-client Python Package](https://pypi.org/project/janus-client/)
- [Bandwidth Estimation and Janus - Meetecho Blog](https://www.meetecho.com/blog/bwe-janus/)

### Mediasoup
- [mediasoup - Official Site](https://mediasoup.org/)
- [versatica/mediasoup - GitHub](https://github.com/versatica/mediasoup)
- [mediasoup Design Documentation](https://mediasoup.org/documentation/v3/mediasoup/design/)
- [mediasoup Scalability Guide](https://mediasoup.org/documentation/v3/scalability/)
- [mediasoup Rust Crate](https://crates.io/crates/mediasoup)
- [pymediasoup - PyPI](https://pypi.org/project/pymediasoup/)
- [CPU/Bandwidth Production Results - Forum](https://mediasoup.discourse.group/t/cpu-bandwidth-results-for-many-to-many-rooms-in-production/4423)

### Pion / LiveKit
- [pion/webrtc - GitHub](https://github.com/pion/webrtc)
- [LiveKit - GitHub](https://github.com/livekit/livekit)
- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Self-Hosting Guide](https://docs.livekit.io/transport/self-hosting/)
- [How Go-based Pion attracted WebRTC Mass - webrtcHacks](https://webrtchacks.com/how-go-based-pion-attracted-webrtc-mass-qa-with-sean-dubois/)
- [Pion WebRTC v4.2.0 Release](https://github.com/pion/webrtc/releases/tag/v4.2.0)

### aiortc
- [aiortc/aiortc - GitHub](https://github.com/aiortc/aiortc)
- [aiortc Python WebRTC Library Guide](https://webrtc.link/en/articles/aiortc-python-webrtc-library/)

### Comparisons & Benchmarks
- [Janus vs Mediasoup vs LiveKit - Trembit](https://trembit.com/blog/choosing-the-right-sfu-janus-vs-mediasoup-vs-livekit-for-telemedicine-platforms/)
- [WebRTC SFU Load Testing - webrtcHacks](https://webrtchacks.com/sfu-load-testing/)
- [CoSMo Comparative Study of WebRTC SFUs](https://mediasoup.org/resources/CoSMo_ComparativeStudyOfWebrtcOpenSourceSfusForVideoConferencing.pdf)
- [WebRTC Video Bitrate Guide - LiveKit](https://livekit.io/webrtc/bitrate-guide)
- [OpenVidu Performance Benchmarks](https://openvidu.io/3.1.0/docs/self-hosting/production-ready/performance/)
