# Mahjong+× — Implementation Plan

Engineering breakdown for the MVP defined in the design doc (Tables 1–2, ~10–15 min run, ~80% of replay value: charms, constellations, spells, shop).

The plan is split into **phases**. Each phase has a clear deliverable and an exit criterion. Phases 0–4 are headless engine work that can ship and be unit-tested without Xcode; phases 5+ require Xcode for the SwiftUI app target.

---

## Architecture

Two Swift modules, one repo:

- **`Engine/`** — pure-Swift Swift Package. No UIKit, no SwiftUI, no Foundation-only-on-Apple imports. Models all game state, rules, scoring, AI, run progression. Fully unit-testable from CLI via `swift test`. Deterministic given a seed.
- **`App/`** — SwiftUI iOS app. Owns rendering, animation, audio, persistence, haptics. Imports `Engine` as a local package. Built in Xcode.

**Why this split:** the engine is the brain of the game and the part most prone to subtle rule bugs. Keeping it pure-Swift and headless means we can iterate on rules with fast tests on any machine, without launching a simulator. The UI layer can be rebuilt or skinned without touching game logic.

**Determinism:** every random source in `Engine/` takes a `RandomNumberGenerator` parameter. The shop, wall, AI tiebreakers, and Boss Wind selection are all reproducible from a seed — needed for daily challenges later, and for repeatable test scenarios now.

**Persistence:** unlock progression, run-in-progress save, and statistics live in `UserDefaults` (small, structured, JSON-encoded). No CoreData / SQLite for MVP — the data is tiny and read-mostly.

**No backend.** Game is fully offline. No accounts, no sync, no analytics for MVP.

---

## Phase 0 — Foundation *(this commit)*

Goal: scaffold the repo, define the tile vocabulary, prove the build/test loop works.

- `Package.swift` with `Engine` library target + `EngineTests` test target
- `Sources/Engine/`: `Suit`, `Wind`, `Dragon`, `Tile`, `TileSet` (standard 144-tile set generator)
- `Tests/EngineTests/`: cover tile equality, Chinese labels, full set composition (144 tiles, correct counts)
- `README.md` with build/test instructions

**Exit:** `swift build` and `swift test` pass cleanly.

---

## Phase 1 — Hand model & pattern detection

Goal: given a set of tiles, decide whether it's a winning hand and what patterns it satisfies.

- `Hand` value type: concealed tiles + exposed melds + bonus tiles
- `Meld` enum: pair, pung, kong, chow
- `Pattern` enum + detector: `dui_dui` (all pairs/pungs), `ping` (all sequences in one suit), `hun_yi_se` (one suit + honors), `qing_yi_se` (pure one suit)
- `HandValidator.isWinning(_:)` — top-level check
- `HandValidator.patterns(in:)` — which patterns the hand satisfies (for scoring)

**Exit:** unit test matrix covering every MVP pattern with positive and negative cases. ≥30 tests.

---

## Phase 2 — Faan scoring

Goal: turn a winning hand into a faan count and a coin payout.

- `FaanCalculator.score(hand:context:)` returns `(faan: Int, breakdown: [FaanReason])`
- Implements the MVP table: 平 = 1, 對對 = 1, 混一色 = 2, 清一色 = 4, flower-matches-seat-wind = +1, self-drawn = +1
- `CoinCalculator.coins(for: faan, table:)` — payout curve (TBD; likely `base * 2^(faan-1)` capped, with table-completion bonus)

**Exit:** scoring tests cover every faan reason in isolation and combined.

---

## Phase 3 — Single-hand state machine

Goal: model one full hand of play (Table 1 Hand 1 — 4 tiles, Cookies only, 1 AI opponent).

- `Wall` — shuffled draw pile, deterministic given a seed
- `HandState` — whose turn, hands, discards, draw pointer
- Player actions: `draw`, `discard(tile)`, `declareWin`
- AI actions: simple "draw, then discard the tile that minimizes shanten" baseline
- Win detection on draw and on opponent discard (claim-win for MVP simplicity; no defensive play yet)

**Exit:** scripted tests run a full hand from initial deal to win, asserting the engine walks through expected states. Hand can be replayed deterministically from a seed.

---

## Phase 4 — Run state & Table 1 progression

Goal: chain four hands into a Table; chain Tables into a run.

- `Run` — table index, hand index, charms, constellations, spells, coin balance, RNG seed
- Hand-by-hand suit/honor unlocks per Table 1 spec (East: Cookies; South: +Bamboo; West: +Characters; North/Boss: +Winds & Dragons)
- Boss hand modifier slot (data only — actual modifiers in Phase 11)
- Run save/restore via `Codable`

**Exit:** can simulate a full Table 1 run headlessly, logging each hand's outcome and coin total.

---

## Phase 5 — SwiftUI app shell *(requires Xcode)*

Goal: get something on screen. Bare-minimum gameplay — render tiles, take turns, show win.

- Xcode project (`MahjongPlusX.xcodeproj`) with one app target depending on the local `Engine` package
- App entry point, root navigation, splash
- Tile view (single tile rendering — placeholder symbols/Chinese chars, no art yet)
- HandView (player's tiles), DiscardPileView, WallCounterView
- Bare gameplay screen for Table 1 Hand 1
- Tap-to-discard interaction

**Exit:** can play a single hand against the AI on a simulator. No styling yet.

---

## Phase 6 — Money & shop UI

Goal: the between-hand shop loop is the most-touched UI in the game; build it early.

- `Shop` engine model: roll 2 charms + 1 booster pack + reroll cost, deterministic from seed
- `ShopView`: SwiftUI screen between hands
- Wallet display, purchase flow, reroll, skip
- Booster pack pick UI (Charm Pack small/large, Constellation Pack, Spell Pack small/mega, Mixed)

**Exit:** can buy charms and packs; coins tracked correctly; shop reflows after each hand.

---

## Phase 7 — Charms (15 starter pool)

Goal: implement all 15 MVP charms and the active-slot system.

- `Charm` data model: id, name, rarity, hook (when it triggers), effect (what it does)
- 5-slot active inventory; sell/swap UI in shop
- Effect engine: charms hook into scoring pipeline (`FaanCalculator` accepts charm context)
- Implement all 15 charms from the design doc spec
- Charm reveal animation in shop (collectible/screenshot-worthy is in scope)

**Exit:** every charm has a unit test that proves its effect at the engine level.

---

## Phase 8 — Constellations (8 starter)

Goal: pattern level-up system.

- `Constellation` data model + 8 starter constellations from the design doc
- Per-pattern level state in `Run` (each pattern starts at L1)
- Consumable slot manager (2 slots shared with Spells)
- Apply constellation: bumps base + mult for the targeted pattern
- Constellation use UI

**Exit:** consuming a constellation persistently raises that pattern's score for the rest of the run.

---

## Phase 9 — Spells (12 starter)

Goal: one-shot tactical effects.

- `Spell` data model + 12 starter spells from the design doc
- Effect engine handles each spell type: tile swap, peek, transform, redraw, joker-add, hand-discard, etc.
- Use UI: drag-to-tile or button-with-target-picker
- Some spells gate on Table (e.g., Charleston Whisper T5+) — gate cleanly so they appear inert in MVP

**Exit:** every spell that's usable in T1–T2 has a working effect end-to-end.

---

## Phase 10 — Table 2

Goal: graduate from "any winning matching setup" to "≥1 faan to win" and bigger hands.

- Hand size grows from 4 to 7 (win on 8th)
- Introduce Chow (T2 H1), Pong (T2 H2), Flowers & Seasons (T2 H3)
- Faan ≥1 requirement enforced for North (T2 H4 Boss) win
- AI gets slightly smarter: prefers tiles that also work toward faan-bearing patterns

**Exit:** a player can win or lose Table 2 according to spec; full MVP run is playable end-to-end.

---

## Phase 11 — Unlock progression

Goal: the meta-game that brings the player back tomorrow.

- `UnlockStore` (UserDefaults-backed) tracks: lifetime tiles discarded, lifetime spells used, hands won by pattern, runs completed, etc.
- Unlock triggers fire at end-of-hand and end-of-run
- Locked items hidden from shop pool entirely
- "New unlock!" celebration UI (small, satisfying — not a popup wall)

**Exit:** the MVP unlock schedule from the design doc fires correctly. New content actually appears in subsequent shops.

---

## Phase 12 — Boss Wind modifiers

Goal: add the 2–3 Boss modifiers called out for first build (Whiteout, Frozen Suit, Long Night).

- `BossWind` enum + effect application during Boss hand setup
- Modifier displayed prominently before Boss hand begins
- Frozen Suit changes win-validity check; Whiteout disables claim-win; Long Night adds turn timer (also requires UI work)

**Exit:** Boss hands feel meaningfully different; unit tests cover each modifier's enforcement.

---

## Phase 13 — Polish

Visual / audio / feel pass. Aesthetic locked in design doc:

- Palm Beach pastel + gold-leaf tile art (commission or stock + retouch)
- Bossa nova background loop + tile clack SFX + rack snap on win
- Charm/Constellation/Spell illustrations (collectible-grade)
- Wind labels show both Chinese + English everywhere
- App icon, launch screen, settings (sound on/off, haptics on/off)
- TestFlight build

**Exit:** ready for closed beta with the target demographic.

---

## Out of scope for MVP (parking lot)

- Tables 3–8, Charleston, defensive AI, multi-AI tables
- Daily challenges, leaderboards, endless mode
- Charm/Constellation/Spell pool expansion beyond starter 15/8/12
- Card Reveal moment (Table 8 finale UX)
- IAP, NMJL partnership, account system

---

## Milestones (suggested order, not a calendar)

| Milestone | Phases | What you can show |
|---|---|---|
| **M0 — Engine foundations** | 0–4 | Headless run simulation, all rules tested |
| **M1 — Playable** | 5–6 | One hand against AI on device, shop visible |
| **M2 — Roguelike loop** | 7–9 | Charms / Constellations / Spells working end-to-end |
| **M3 — MVP feature-complete** | 10–12 | Full Tables 1–2 run, unlocks, Boss modifiers |
| **M4 — Beta-ready** | 13 | Polished, on TestFlight |
