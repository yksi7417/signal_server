/// Per-(Table, Hand) configuration for the MVP.
///
/// Tables 1–2 implement the design doc's "First Steps" and "The Real Game
/// Begins" arcs. Tables 3–8 are post-MVP per the design doc.
public enum TableProgression {

    /// Build a `HandConfig` for the given Table+Hand position.
    ///
    /// `bossModifier` is honored only when this is the 4th hand of the Table.
    public static func handConfig(
        table: Int,
        hand: Int,
        bossModifier: BossModifier? = nil
    ) -> HandConfig {
        let prevailing: Wind = {
            switch hand {
            case 1: return .east
            case 2: return .south
            case 3: return .west
            case 4: return .north
            default: return .east
            }
        }()
        let isBoss = (hand == 4)
        switch table {
        case 1:
            return HandConfig(
                table: 1,
                handIndex: hand,
                prevailingWind: prevailing,
                handSize: 4,
                minFaanToWin: 0,
                allowsChow: false,
                allowsPong: false,
                allowsClaimWin: true,
                bonusTilesEnabled: false,
                bossModifier: isBoss ? bossModifier : nil
            )
        case 2:
            return HandConfig(
                table: 2,
                handIndex: hand,
                prevailingWind: prevailing,
                handSize: 7,
                // Boss enforces ≥1 faan to win per design.
                minFaanToWin: isBoss ? 1 : 0,
                allowsChow: hand >= 1,
                allowsPong: hand >= 2,
                allowsClaimWin: true,
                // Flowers/Seasons introduced at T2H3.
                bonusTilesEnabled: hand >= 3,
                bossModifier: isBoss ? bossModifier : nil
            )
        default:
            preconditionFailure("Table \(table) not in MVP — see Phase 2/3 of IMPLEMENTATION_PLAN.md")
        }
    }

    /// Wall tile pool for the given Table+Hand. Per design doc:
    ///   T1H1: Cookies only
    ///   T1H2: + Bamboo
    ///   T1H3: + Characters
    ///   T1H4: + Winds & Dragons
    ///   T2H1, T2H2: number suits + honors (no bonus)
    ///   T2H3, T2H4: full standard set including bonus tiles
    public static func wallTiles(table: Int, hand: Int) -> [Tile] {
        switch (table, hand) {
        case (1, 1):
            return TileSet.singleSuit(.cookies)
        case (1, 2):
            return TileSet.suits([.cookies, .bamboo])
        case (1, 3):
            return TileSet.suits([.cookies, .bamboo, .characters])
        case (1, 4):
            return TileSet.suits([.cookies, .bamboo, .characters]) + TileSet.honors()
        case (2, 1), (2, 2):
            return TileSet.suits([.cookies, .bamboo, .characters]) + TileSet.honors()
        case (2, 3), (2, 4):
            return TileSet.standard()
        default:
            preconditionFailure("Invalid (table, hand) = (\(table), \(hand))")
        }
    }

    /// MVP boss-modifier kind pool — picked from the design doc's first build list.
    public static let bossKindPool: [BossModifier.Kind] = [.whiteout, .frozenSuit, .longNight]

    /// Pick a boss modifier deterministically. Returns nil if `pool` is empty.
    /// For `.frozenSuit`, also picks which suit is frozen.
    public static func rollBossModifier<G: RandomNumberGenerator>(
        rng: inout G,
        pool: [BossModifier.Kind] = bossKindPool
    ) -> BossModifier? {
        guard !pool.isEmpty else { return nil }
        let kind = pool[Int.random(in: 0..<pool.count, using: &rng)]
        switch kind {
        case .whiteout:    return .whiteout
        case .longNight:   return .longNight
        case .frozenSuit:
            let suit = Suit.allCases[Int.random(in: 0..<Suit.allCases.count, using: &rng)]
            return .frozenSuit(suit)
        }
    }

    /// Total Tables in the MVP run.
    public static let mvpTableCount = 2
    /// Hands per Table.
    public static let handsPerTable = 4
}
