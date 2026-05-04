/// Persistent unlock progression — what charms / constellations / spells the
/// player has access to in shops. Drives the meta-game.
///
/// `UnlockStore` is engine-only state. The host (iOS app) is responsible for
/// persisting it to UserDefaults / iCloud key-value store.
///
/// MVP unlock schedule from the design doc:
///   - Game start: 6 Charms, 4 Constellations, 6 Spells
///   - Win first hand: +1 Charm
///   - Win Table 1: +2 Charms, +1 Constellation, +1 Spell
///   - Win Table 2 (full MVP run): +3 Charms, +2 Constellations, +3 Spells
///   - Discard 50 tiles total: +1 Charm
///   - Score 100+ in a single hand: +1 rare Charm
///   - Win without losing a hand: +1 legendary Charm
///   - Use 10 Spells total: +2 Spells
///   - Win with 清一色: +1 Constellation
public struct UnlockStore: Codable, Sendable, Hashable {
    public var unlockedCharmIDs: Set<String>
    public var unlockedConstellationIDs: Set<String>
    public var unlockedSpellIDs: Set<String>

    /// Lifetime aggregate stats used to fire unlock triggers.
    public var lifetimeStats: LifetimeStats

    public init() {
        let starter = Self.starterUnlocks()
        self.unlockedCharmIDs = starter.charms
        self.unlockedConstellationIDs = starter.constellations
        self.unlockedSpellIDs = starter.spells
        self.lifetimeStats = LifetimeStats()
    }

    public struct LifetimeStats: Codable, Sendable, Hashable {
        public var handsWon: Int = 0
        public var firstHandWonEver: Bool = false
        public var tablesCleared: Set<Int> = []        // by Table number
        public var lifetimeDiscards: Int = 0
        public var spellsUsed: Int = 0
        public var winsByPattern: [Pattern: Int] = [:]
        public var maxScoreInOneHand: Int = 0
        public var sweepRunsCompleted: Int = 0          // boss-clean runs
        public var fullRunsCompleted: Int = 0
        public init() {}
    }

    /// Build a starter unlock set per design doc: 6 charms, 4 constellations, 6 spells.
    /// Picks deterministically from the catalogs by canonical order.
    public static func starterUnlocks() -> (charms: Set<String>, constellations: Set<String>, spells: Set<String>) {
        let charms = Set(CharmCatalog.starter.prefix(6).map(\.id))
        let consts = Set(ConstellationCatalog.starter.prefix(4).map(\.id))
        let spells = Set(SpellCatalog.starter.prefix(6).map(\.id))
        return (charms, consts, spells)
    }

    /// Unlocks fired by a single hand outcome and run state. Returns the
    /// list of newly-unlocked items for UI celebration.
    @discardableResult
    public mutating func recordHand(
        result: HandResult,
        run: Run
    ) -> [Unlock] {
        var fresh: [Unlock] = []

        // Aggregate updates.
        if result.playerWon {
            lifetimeStats.handsWon += 1
            if let pattern = result.primaryPattern {
                lifetimeStats.winsByPattern[pattern, default: 0] += 1
            }
            if !lifetimeStats.firstHandWonEver {
                lifetimeStats.firstHandWonEver = true
                fresh += unlockNext(.charm, count: 1, fromCatalog: CharmCatalog.starter)
            }
            if result.score > lifetimeStats.maxScoreInOneHand {
                lifetimeStats.maxScoreInOneHand = result.score
                if result.score >= 100 {
                    fresh += unlockNext(.charm, count: 1, fromCatalog: CharmCatalog.charms(by: .rare))
                }
            }
            if result.primaryPattern == .qingYiSe {
                fresh += unlockNext(.constellation, count: 1, fromCatalog: ConstellationCatalog.starter)
            }
        }
        lifetimeStats.lifetimeDiscards += result.discardsThisHand
        if lifetimeStats.lifetimeDiscards >= 50 && !hasMilestone("discards50") {
            fresh += unlockNext(.charm, count: 1, fromCatalog: CharmCatalog.starter)
            milestones.insert("discards50")
        }

        lifetimeStats.spellsUsed += result.spellsUsedThisHand
        if lifetimeStats.spellsUsed >= 10 && !hasMilestone("spells10") {
            fresh += unlockNext(.spell, count: 2, fromCatalog: SpellCatalog.starter)
            milestones.insert("spells10")
        }

        // Table clear.
        if run.currentTable.isComplete {
            if run.currentTable.didSweep || run.currentTable.handsWon > 0 {
                if !lifetimeStats.tablesCleared.contains(run.table) {
                    lifetimeStats.tablesCleared.insert(run.table)
                    fresh += unlocksForTableCleared(run.table)
                }
            }
        }

        // Full run completion.
        if run.status == .completed && !hasMilestone("fullRun") {
            lifetimeStats.fullRunsCompleted += 1
            milestones.insert("fullRun")
        }

        // Sweep run (won every hand of every Table).
        if run.status == .completed
            && run.stats.handsLost == 0
            && !hasMilestone("sweepRun") {
            lifetimeStats.sweepRunsCompleted += 1
            milestones.insert("sweepRun")
            fresh += unlockNext(.charm, count: 1, fromCatalog: CharmCatalog.charms(by: .legendary))
        }

        return fresh
    }

    public var milestones: Set<String> {
        get { _milestones }
        set { _milestones = newValue }
    }
    private var _milestones: Set<String> = []

    private func hasMilestone(_ id: String) -> Bool { _milestones.contains(id) }

    private mutating func unlocksForTableCleared(_ table: Int) -> [Unlock] {
        switch table {
        case 1:
            return unlockNext(.charm, count: 2, fromCatalog: CharmCatalog.starter)
                + unlockNext(.constellation, count: 1, fromCatalog: ConstellationCatalog.starter)
                + unlockNext(.spell, count: 1, fromCatalog: SpellCatalog.starter)
        case 2:
            return unlockNext(.charm, count: 3, fromCatalog: CharmCatalog.starter)
                + unlockNext(.constellation, count: 2, fromCatalog: ConstellationCatalog.starter)
                + unlockNext(.spell, count: 3, fromCatalog: SpellCatalog.starter)
        default:
            return []
        }
    }

    /// Unlock up to `count` items from `catalog` that aren't already unlocked.
    private mutating func unlockNext(_ kind: Unlock.Kind, count: Int, fromCatalog catalog: [some Identifiable]) -> [Unlock] {
        var fresh: [Unlock] = []
        for item in catalog {
            if fresh.count >= count { break }
            let id = String(describing: item.id)
            switch kind {
            case .charm:
                if unlockedCharmIDs.insert(id).inserted {
                    fresh.append(.init(kind: .charm, id: id))
                }
            case .constellation:
                if unlockedConstellationIDs.insert(id).inserted {
                    fresh.append(.init(kind: .constellation, id: id))
                }
            case .spell:
                if unlockedSpellIDs.insert(id).inserted {
                    fresh.append(.init(kind: .spell, id: id))
                }
            }
        }
        return fresh
    }

    /// What's currently unlocked, materialized for shop rolls.
    public var pool: UnlockedPool {
        UnlockedPool(
            charms: CharmCatalog.starter.filter { unlockedCharmIDs.contains($0.id) },
            constellations: ConstellationCatalog.starter.filter { unlockedConstellationIDs.contains($0.id) },
            spells: SpellCatalog.starter.filter { unlockedSpellIDs.contains($0.id) }
        )
    }
}

/// A single unlock event — used for celebration UI.
public struct Unlock: Codable, Sendable, Hashable {
    public enum Kind: String, Codable, Sendable, Hashable {
        case charm, constellation, spell
    }
    public let kind: Kind
    public let id: String
    public init(kind: Kind, id: String) { self.kind = kind; self.id = id }
}

/// What the engine reports back to the unlock store at end of hand.
public struct HandResult: Sendable {
    public var playerWon: Bool
    public var primaryPattern: Pattern?
    public var score: Int
    public var discardsThisHand: Int
    public var spellsUsedThisHand: Int

    public init(
        playerWon: Bool,
        primaryPattern: Pattern? = nil,
        score: Int = 0,
        discardsThisHand: Int = 0,
        spellsUsedThisHand: Int = 0
    ) {
        self.playerWon = playerWon
        self.primaryPattern = primaryPattern
        self.score = score
        self.discardsThisHand = discardsThisHand
        self.spellsUsedThisHand = spellsUsedThisHand
    }
}
