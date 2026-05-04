/// Cumulative stats for a Run. Drives unlock progression and end-of-run summary.
public struct RunStats: Codable, Sendable, Hashable {
    public var handsWon: Int = 0
    public var handsLost: Int = 0
    public var totalCoinsEarned: Int = 0
    public var totalCoinsSpent: Int = 0
    public var totalFaan: Int = 0
    public var lifetimeDiscards: Int = 0
    public var spellsUsed: Int = 0
    public var tableSweepCount: Int = 0
    public var maxScoreInOneHand: Int = 0
    public var winsByPattern: [Pattern: Int] = [:]

    public init() {}
}

/// Per-table progress within a run. Resets at the start of each Table.
public struct TableProgress: Codable, Sendable, Hashable {
    public var handsWon: Int = 0
    public var handsLost: Int = 0
    public var bossModifier: BossModifier?

    public init(bossModifier: BossModifier? = nil) {
        self.bossModifier = bossModifier
    }

    /// True if all 4 hands of the Table were won.
    public var didSweep: Bool { handsWon == TableProgression.handsPerTable && handsLost == 0 }
    /// True if the Table is complete (4 hands resolved either way).
    public var isComplete: Bool { (handsWon + handsLost) >= TableProgression.handsPerTable }
}
