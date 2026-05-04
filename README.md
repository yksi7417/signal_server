# Mahjong+×

A solo, offline mahjong trainer for iOS — disguised as a roguelike.

Built for the American Mahjong social-club player who wants to practice between game nights. Inspired by *Balatro*'s core loop: deeply strategic, endlessly replayable, satisfying enough to play on a plane.

> **Status:** very early. Phase 0 (engine foundation) is the current build. See [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) for the full roadmap.

---

## Repository layout

```
.
├── Package.swift             # Swift Package manifest — Engine library + tests
├── Sources/
│   └── Engine/               # Pure-Swift game engine (no UIKit/SwiftUI)
└── Tests/
    └── EngineTests/          # XCTest suite for the engine
```

The iOS app target (`App/`, `MahjongPlusX.xcodeproj`) will be added in Phase 5 once UI work begins. See [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md#architecture) for the rationale on the engine/app split.

---

## Build & test

The engine is a plain Swift Package — no Xcode required.

```bash
swift build
swift test
```

Tested with Swift 6.1 on macOS. The engine intentionally has zero dependencies.

---

## Design

Core design doc lives in the project — game concept, table progression, tile vocabulary, charm/constellation/spell pools, shop mechanics, unlock schedule, and aesthetic guidelines.

A few key decisions worth knowing up front:

- **Offline-first.** No accounts, no backend, no sync. Everything runs on the device.
- **Determinism.** Every random source takes a `RandomNumberGenerator` parameter so runs can be replayed from a seed (needed for the daily challenge later, useful for tests now).
- **Engine ↔ UI split.** Game rules are pure Swift, fully unit-testable from CLI. SwiftUI layer is a thin renderer over a state machine.

---

## Naming

- Product name: **MahjongPlusX**
- Logo / stylized: Mahjong+× or Mahjong+X
- Spoken: "Mahjong Plus X"

The "+×" nods to mahjong scoring (faan = base × multiplier) and to the meta-game's roguelike combinatorial space.
