/// Full run state — the player's progress across all Tables.
///
/// Owns:
///   - RNG seed (for reproducible runs / daily challenges later)
///   - Table & hand position
///   - Coin balance
///   - Active charms (≤5), consumables (≤2 spells/constellations combined)
///   - Pattern level bumps (from Constellations)
///   - Stats (driven by `Run.recordHandOutcome(_:)`)
///   - Status (in-progress / complete / failed)
public struct Run: Codable, Sendable {

    public let seed: UInt64
    public var rng: SeededRandomNumberGenerator
    public var status: Status

    public var table: Int
    public var handIndex: Int   // 1–4 within the current Table
    public var coins: Int

    public var charms: [Charm]                // active, ≤ slots.charms
    public var consumables: [Consumable]      // active spells + constellations, ≤ slots.consumables

    public var patternBumps: [Pattern: PatternBumps]
    public var bonusBaseBumpFromConstellations: Int  // Andromeda contribution

    public var stats: RunStats
    public var currentTable: TableProgress

    public var pendingNextHandMult: Double    // e.g. Four Winds Aligned sweep bonus
    public var spellsUsedThisRun: Int { stats.spellsUsed }

    public static let slots = Slots(charms: 5, consumables: 2)

    public struct Slots: Codable, Sendable, Hashable {
        public let charms: Int
        public let consumables: Int
    }

    public enum Status: String, Codable, Sendable, Hashable {
        case inProgress
        case completed   // beat all MVP Tables
        case failed      // boss loss path (post-MVP)
    }

    public init(seed: UInt64) {
        self.seed = seed
        self.rng = SeededRandomNumberGenerator(seed: seed)
        self.status = .inProgress
        self.table = 1
        self.handIndex = 1
        self.coins = 0
        self.charms = []
        self.consumables = []
        self.patternBumps = [:]
        self.bonusBaseBumpFromConstellations = 0
        self.stats = RunStats()
        self.currentTable = TableProgress()
        self.pendingNextHandMult = 1.0
    }

    /// Build a `HandConfig` for the run's current position. Re-rolls the boss
    /// modifier if this is a boss hand and one isn't yet assigned.
    public mutating func currentHandConfig() -> HandConfig {
        if handIndex == TableProgression.handsPerTable && currentTable.bossModifier == nil {
            currentTable.bossModifier = TableProgression.rollBossModifier(rng: &rng)
        }
        return TableProgression.handConfig(
            table: table,
            hand: handIndex,
            bossModifier: currentTable.bossModifier
        )
    }

    /// The wall tile pool for the current position.
    public var currentWallTiles: [Tile] {
        TableProgression.wallTiles(table: table, hand: handIndex)
    }

    /// Build the current `HandState` ready for play.
    public mutating func startHand() -> HandState {
        let config = currentHandConfig()
        let tiles = currentWallTiles
        return HandState.deal(config: config, wallTiles: tiles, rng: &rng)
    }

    // MARK: - Outcome recording

    /// Record the outcome of a finished hand. Updates stats, coins, advances
    /// to the next hand or the next Table, and finalises the run when done.
    public mutating func recordHandOutcome(_ state: HandState) {
        guard state.phase == .ended else { return }
        switch state.outcome {
        case .win(let seat, let score, _):
            if seat == .player {
                recordPlayerWin(score: score)
            } else {
                recordPlayerLoss()
            }
        case .wallExhausted:
            // No-win, no-loss — advance without affecting sweep count.
            // Treat as "lost hand" for sweep purposes (no win, so not a sweep).
            currentTable.handsLost += 1
            stats.handsLost += 1
        case nil:
            return
        }
        advance()
    }

    private mutating func recordPlayerWin(score: FaanScore) {
        // Compute base × mult coins via ScoringEngine. We need to re-score
        // here to capture charm/pattern-level effects (the HandEngine only
        // uses FaanCalculator for its win-threshold gate).
        // Caller should have already used `scoreCurrentWin(state:)` if they
        // need the full breakdown. Here we just take faan as a fallback.
        let faan = score.faan
        var coins = CoinCalculator.coins(for: score)

        // Per-charm coin bonuses.
        for charm in charms {
            if case .coinsPerWin(let amt) = charm.effect { coins += amt }
        }
        self.coins += coins
        stats.totalCoinsEarned += coins
        stats.handsWon += 1
        stats.totalFaan += faan
        currentTable.handsWon += 1
        for reason in score.reasons {
            // Pattern-by-name detection (cheap; reasons carry the chinese name).
            for p in Pattern.allCases where p.chinese == reason.label {
                stats.winsByPattern[p, default: 0] += 1
            }
        }
    }

    private mutating func recordPlayerLoss() {
        currentTable.handsLost += 1
        stats.handsLost += 1
    }

    /// Advance hand/table position. Triggers Table sweep bonus + boss roll.
    public mutating func advance() {
        if currentTable.isComplete {
            // End of Table.
            if currentTable.didSweep {
                let bonus = CoinCalculator.tableCompletionBonus(swept: true)
                coins += bonus
                stats.totalCoinsEarned += bonus
                stats.tableSweepCount += 1

                // Apply nextTableSweepMult charm pendingly.
                for charm in charms {
                    if case .nextTableSweepMult(let factor) = charm.effect {
                        pendingNextHandMult *= factor
                    }
                }
            }
            // Move to next Table.
            if table >= TableProgression.mvpTableCount {
                status = .completed
            } else {
                table += 1
                handIndex = 1
                currentTable = TableProgress()
            }
        } else {
            handIndex += 1
        }
    }

    // MARK: - Inventory

    public var canAddCharm: Bool { charms.count < Self.slots.charms }
    public var canAddConsumable: Bool { consumables.count < Self.slots.consumables }

    /// Add a charm to the active inventory. Returns false if no slot free or duplicate id.
    @discardableResult
    public mutating func addCharm(_ charm: Charm) -> Bool {
        guard canAddCharm, !charms.contains(where: { $0.id == charm.id }) else { return false }
        charms.append(charm)
        return true
    }

    @discardableResult
    public mutating func removeCharm(id: String) -> Bool {
        guard let idx = charms.firstIndex(where: { $0.id == id }) else { return false }
        charms.remove(at: idx)
        return true
    }

    @discardableResult
    public mutating func addConsumable(_ c: Consumable) -> Bool {
        guard canAddConsumable else { return false }
        consumables.append(c)
        return true
    }

    /// Use a consumable. Returns true if applied; consumable is removed on success.
    @discardableResult
    public mutating func useConsumable(id: String) -> Bool {
        guard let idx = consumables.firstIndex(where: { $0.id == id }) else { return false }
        let consumable = consumables[idx]
        switch consumable {
        case .constellation(let c):
            applyConstellation(c)
        case .spell:
            stats.spellsUsed += 1
        }
        consumables.remove(at: idx)
        return true
    }

    private mutating func applyConstellation(_ c: Constellation) {
        switch c.target {
        case .pattern(let p):
            patternBumps[p, default: PatternBumps()].apply(base: c.baseDelta, mult: c.multDelta)
        case .allPatterns:
            for p in Pattern.allCases {
                patternBumps[p, default: PatternBumps()].apply(base: c.baseDelta, mult: c.multDelta)
            }
        case .bonusTiles:
            bonusBaseBumpFromConstellations += c.baseDelta
        }
    }

    // MARK: - Scoring helpers

    /// Build `ScoringInputs` for a given hand outcome under this run's state.
    public func scoringInputs(
        for hand: Hand,
        seatWind: Wind,
        prevailingWind: Wind,
        selfDrawn: Bool
    ) -> ScoringInputs {
        ScoringInputs(
            hand: hand,
            seatWind: seatWind,
            prevailingWind: prevailingWind,
            selfDrawn: selfDrawn,
            charms: charms,
            patternBumps: patternBumps,
            spellsUsedThisRun: spellsUsedThisRun,
            bonusBaseBumpFromConstellations: bonusBaseBumpFromConstellations
        )
    }

    /// Score a winning HandState through the run's full scoring engine.
    /// Updates stats.maxScoreInOneHand if applicable.
    public mutating func scorePlayerWin(in state: HandState) -> ScoringResult {
        guard case .win(let seat, _, let from) = state.outcome, seat == .player else {
            return ScoringResult(faan: 0, base: 0, mult: 0, total: 0, events: [], primaryPattern: nil)
        }
        let inputs = scoringInputs(
            for: state.hand(for: .player),
            seatWind: Seat.player.defaultSeatWind,
            prevailingWind: state.config.prevailingWind,
            selfDrawn: from == nil
        )
        var result = ScoringEngine.score(inputs)
        // Apply pending sweep multiplier (one-shot, on the first hand of a Table).
        if pendingNextHandMult > 1.0 && handIndex == 1 {
            let boostedTotal = Int((Double(result.base) * result.mult * pendingNextHandMult).rounded())
            result = ScoringResult(
                faan: result.faan, base: result.base, mult: result.mult * pendingNextHandMult,
                total: boostedTotal, events: result.events + [
                    ScoreEvent(label: "Sweep Bonus", multFactor: pendingNextHandMult)
                ], primaryPattern: result.primaryPattern
            )
            pendingNextHandMult = 1.0
        }
        stats.maxScoreInOneHand = max(stats.maxScoreInOneHand, result.total)
        return result
    }
}
