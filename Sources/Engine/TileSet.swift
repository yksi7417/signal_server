/// Builders for the standard tile collection used to seed a wall.
///
/// Standard set (144 tiles):
///   - 3 suits × 9 ranks × 4 copies = 108
///   - 4 winds × 4 copies            =  16
///   - 3 dragons × 4 copies          =  12
///   - 4 flowers + 4 seasons         =   8
///
/// Jokers are not part of the standard set — they enter play only via
/// spells or higher-Table configurations.
public enum TileSet {
    /// The full 144-tile set, in canonical (deterministic) order.
    /// Shuffle the result with a seeded RNG when building a wall.
    public static func standard() -> [Tile] {
        var tiles: [Tile] = []
        tiles.reserveCapacity(144)

        for suit in Suit.allCases {
            for rank in 1...9 {
                for _ in 0..<4 {
                    tiles.append(.suited(suit, rank: rank))
                }
            }
        }
        for wind in Wind.allCases {
            for _ in 0..<4 { tiles.append(.wind(wind)) }
        }
        for dragon in Dragon.allCases {
            for _ in 0..<4 { tiles.append(.dragon(dragon)) }
        }
        for n in 1...4 { tiles.append(.flower(n)) }
        for n in 1...4 { tiles.append(.season(n)) }

        return tiles
    }

    /// MVP Table 1 Hand 1 set: Cookies only, 4 copies of each rank (36 tiles).
    /// No honors, no bonus tiles. Used for the "First Steps" introductory hand.
    public static func table1Hand1() -> [Tile] {
        singleSuit(.cookies)
    }

    /// 4 copies of each rank 1–9 of one number suit (36 tiles).
    public static func singleSuit(_ suit: Suit) -> [Tile] {
        var tiles: [Tile] = []
        tiles.reserveCapacity(36)
        for rank in 1...9 {
            for _ in 0..<4 { tiles.append(.suited(suit, rank: rank)) }
        }
        return tiles
    }

    /// Concatenated `singleSuit` for each suit in `suits` (no dedup).
    public static func suits(_ suits: [Suit]) -> [Tile] {
        suits.flatMap(singleSuit)
    }

    /// Honor tiles only (winds + dragons), 4 copies each (28 tiles).
    public static func honors() -> [Tile] {
        var tiles: [Tile] = []
        tiles.reserveCapacity(28)
        for w in Wind.allCases { for _ in 0..<4 { tiles.append(.wind(w)) } }
        for d in Dragon.allCases { for _ in 0..<4 { tiles.append(.dragon(d)) } }
        return tiles
    }

    /// Flowers + seasons (8 tiles, one of each).
    public static func bonusTiles() -> [Tile] {
        (1...4).map { Tile.flower($0) } + (1...4).map { Tile.season($0) }
    }
}
