import Testing
@testable import Engine

@Suite("Full-run integration")
struct FullRunIntegrationTests {

    /// Plays an entire MVP run (Tables 1–2, 8 hands) headlessly, both seats
    /// driven by SimpleAI. Asserts the run terminates in `.completed` status
    /// and exactly 8 hands have been resolved.
    @Test func fullRunCompletes() throws {
        var run = Run(seed: 12345)
        var rng = SeededRandomNumberGenerator(seed: 12345 &* 31 + 7)
        var iterations = 0
        let safetyLimit = 100   // ≤100 hands ever

        while run.status == .inProgress && iterations < safetyLimit {
            iterations += 1
            var state = run.startHand()
            try RunDriver.playHandWithSimpleAI(state: &state, rng: &rng)
            run.recordHandOutcome(state)
        }

        #expect(run.status == .completed)
        #expect(run.stats.handsWon + run.stats.handsLost == 8)
        #expect(iterations <= 8)
    }

    /// Determinism: two runs with the same seed produce identical stats.
    @Test func sameSeedProducesIdenticalRuns() throws {
        func play(seed: UInt64) throws -> RunStats {
            var run = Run(seed: seed)
            var rng = SeededRandomNumberGenerator(seed: seed &* 31 + 7)
            while run.status == .inProgress {
                var state = run.startHand()
                try RunDriver.playHandWithSimpleAI(state: &state, rng: &rng)
                run.recordHandOutcome(state)
            }
            return run.stats
        }
        let a = try play(seed: 7)
        let b = try play(seed: 7)
        #expect(a == b)
    }

    /// Different seeds produce different outcomes (probabilistic — sample many).
    @Test func differentSeedsProduceDifferentOutcomes() throws {
        var stats: Set<Int> = []
        for seed: UInt64 in 1...20 {
            var run = Run(seed: seed)
            var rng = SeededRandomNumberGenerator(seed: seed &* 31 + 7)
            while run.status == .inProgress {
                var state = run.startHand()
                try RunDriver.playHandWithSimpleAI(state: &state, rng: &rng)
                run.recordHandOutcome(state)
            }
            stats.insert(run.stats.handsWon * 100 + run.stats.totalCoinsEarned)
        }
        // Across 20 seeds, expect at least 5 distinct (handsWon, coins) signatures.
        #expect(stats.count >= 5)
    }

    /// With charms equipped, scoring exceeds bare-bones runs.
    @Test func charmsBoostScoring() throws {
        func runWithCharms(_ charmIDs: [String]) throws -> Int {
            var run = Run(seed: 100)
            for id in charmIDs {
                if let c = CharmCatalog.charm(id: id) { _ = run.addCharm(c) }
            }
            var rng = SeededRandomNumberGenerator(seed: 100 &* 31 + 7)
            while run.status == .inProgress {
                var state = run.startHand()
                try RunDriver.playHandWithSimpleAI(state: &state, rng: &rng)
                run.recordHandOutcome(state)
            }
            return run.stats.maxScoreInOneHand
        }
        let bare = try runWithCharms([])
        let boosted = try runWithCharms(["pung_power", "pair_charm", "the_hostess"])
        // Boosted run's max score is at least as high as the bare-bones run.
        // (RNG is identical so the same hand wins the same way; charms add to it.)
        #expect(boosted >= bare)
    }

    /// Constellations applied before play raise pattern stats and can lift scores.
    @Test func constellationsApplyToScoring() throws {
        var run = Run(seed: 200)
        // Stack heavy boosts on 清一色: Phoenix + Draco
        if let phoenix = ConstellationCatalog.constellation(id: "phoenix") {
            _ = run.addConsumable(.constellation(phoenix))
            _ = run.useConsumable(id: "c:phoenix")
        }
        if let draco = ConstellationCatalog.constellation(id: "draco") {
            _ = run.addConsumable(.constellation(draco))
            _ = run.useConsumable(id: "c:draco")
        }
        let bumps = run.patternBumps[.qingYiSe]!
        // Phoenix(+20, +1.0) + Draco(+30, +1.5) = (+50, +2.5)
        #expect(bumps.baseDelta == 50)
        #expect(bumps.multDelta == 2.5)
    }

    /// Smoke test: across 50 seeds the simulator never deadlocks or runs away.
    @Test func noDeadlockAcrossManySeeds() throws {
        for seed: UInt64 in 1...50 {
            var run = Run(seed: seed)
            var rng = SeededRandomNumberGenerator(seed: seed &* 31 + 7)
            while run.status == .inProgress {
                var state = run.startHand()
                try RunDriver.playHandWithSimpleAI(state: &state, rng: &rng)
                run.recordHandOutcome(state)
            }
            #expect(run.status == .completed)
        }
    }
}
