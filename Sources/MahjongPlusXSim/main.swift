import Engine

// Headless full-run simulator. Plays through Tables 1–2 with the Simple AI
// driving both seats, prints hand-by-hand outcomes and a final summary.
//
// Usage:
//   swift run mahjong-plusx-sim [seed]
//
// Defaults to seed 12345 if none supplied.

let seed: UInt64 = {
    if CommandLine.arguments.count >= 2, let parsed = UInt64(CommandLine.arguments[1]) {
        return parsed
    }
    return 12345
}()

print("Mahjong+× — headless run simulation")
print("Seed: \(seed)")
print(String(repeating: "─", count: 60))

var run = Run(seed: seed)
var unlocks = UnlockStore()

// Pre-equip a few starter charms for a more interesting run.
let starterEquip = [
    "the_hostess",       // +5 coins per win
    "pair_charm",        // +15 base per pair
    "pung_power",        // ×1.5 mult per pung
]
for id in starterEquip {
    if let charm = CharmCatalog.charm(id: id) { _ = run.addCharm(charm) }
}

// And one constellation in the slot.
if let orion = ConstellationCatalog.constellation(id: "orion") {
    _ = run.addConsumable(.constellation(orion))
}

// Use it before the first hand to bump 對對.
_ = run.useConsumable(id: "c:orion")

print("Starting charms: \(run.charms.map(\.name).joined(separator: ", "))")
print("")

var rng = SeededRandomNumberGenerator(seed: seed &* 31 + 7)

handLoop: while run.status == .inProgress {
    var state = run.startHand()
    let cfg = state.config
    print("Table \(cfg.table), Hand \(cfg.handIndex) — \(cfg.prevailingWind.label)" +
          (cfg.isBossHand ? " 👑 BOSS" : ""))
    if let boss = cfg.bossModifier {
        print("  Boss modifier: \(boss.displayName) — \(boss.description)")
    }
    print("  Wall: \(state.wall.remaining) tiles, hand size: \(cfg.handSize)")

    do {
        _ = try RunDriver.playHandWithSimpleAI(state: &state, rng: &rng)
    } catch RunDriverError.runawayLoop(let iters) {
        print("  ⚠️  runaway loop after \(iters) iterations — abandoning hand.")
        break handLoop
    } catch HandActionError.wallExhausted {
        // Already reflected in state.outcome.
    } catch {
        print("  ⚠️  engine error: \(error)")
        break handLoop
    }

    // Compute the result via run-aware scoring (charms + pattern bumps).
    var result = HandResult(playerWon: false)
    switch state.outcome {
    case .win(let seat, let faanScore, let from):
        if seat == .player {
            let scored = run.scorePlayerWin(in: state)
            print("  ✓ Player wins! \(scored.primaryPattern?.chinese ?? "?")"
                + " — base \(scored.base) × mult \(scored.mult) = \(scored.total)"
                + " (faan \(scored.faan), \(from == nil ? "self-drawn" : "claim"))")
            result = HandResult(
                playerWon: true,
                primaryPattern: scored.primaryPattern,
                score: scored.total,
                discardsThisHand: state.discards.count,
                spellsUsedThisHand: 0
            )
        } else {
            print("  ✗ AI wins. faan \(faanScore.faan)")
            result = HandResult(
                playerWon: false,
                discardsThisHand: state.discards.count
            )
        }
    case .wallExhausted:
        print("  · Wall exhausted — no win.")
        result = HandResult(playerWon: false, discardsThisHand: state.discards.count)
    case nil:
        print("  ? Hand ended without outcome.")
    }

    run.recordHandOutcome(state)
    let unlocked = unlocks.recordHand(result: result, run: run)
    if !unlocked.isEmpty {
        for u in unlocked {
            print("  🌟 unlocked: \(u.kind.rawValue) \(u.id)")
        }
    }
    print("  Coins: \(run.coins) | record: \(run.stats.handsWon)W \(run.stats.handsLost)L")
    print("")
}

print(String(repeating: "─", count: 60))
print("Run complete — status: \(run.status.rawValue)")
print("  Hands won:  \(run.stats.handsWon)")
print("  Hands lost: \(run.stats.handsLost)")
print("  Total coins earned: \(run.stats.totalCoinsEarned)")
print("  Max single-hand score: \(run.stats.maxScoreInOneHand)")
print("  Wins by pattern: \(run.stats.winsByPattern)")
print("  Tables swept: \(run.stats.tableSweepCount)")
print("  Lifetime unlocks: charms=\(unlocks.unlockedCharmIDs.count)" +
      ", constellations=\(unlocks.unlockedConstellationIDs.count)" +
      ", spells=\(unlocks.unlockedSpellIDs.count)")
