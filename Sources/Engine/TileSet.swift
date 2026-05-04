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
        var tiles: [Tile] = []
        tiles.reserveCapacity(36)
        for rank in 1...9 {
            for _ in 0..<4 {
                tiles.append(.suited(.cookies, rank: rank))
            }
        }
        return tiles
    }
}
