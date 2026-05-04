/// A player's hand: concealed (in-hand) tiles, exposed (declared) melds,
/// and bonus tiles set aside (flowers/seasons).
public struct Hand: Hashable, Codable, Sendable {
    public var concealed: [Tile]
    public var melds: [Meld]
    public var bonus: [Tile]

    public init(concealed: [Tile] = [], melds: [Meld] = [], bonus: [Tile] = []) {
        self.concealed = concealed
        self.melds = melds
        self.bonus = bonus
    }

    /// All tiles "in play" — concealed plus tiles inside declared melds.
    /// Bonus tiles are excluded; they score separately.
    public var playTiles: [Tile] {
        concealed + melds.flatMap(\.tiles)
    }

    /// Total in-play tile count. Used for win-size checks (e.g. T1 = 5, T2 = 8).
    public var size: Int { playTiles.count }

    // MARK: - Mutation helpers

    public mutating func draw(_ tile: Tile) {
        concealed.append(tile)
    }

    /// Removes a single matching tile from `concealed`. Returns true if found.
    @discardableResult
    public mutating func discard(_ tile: Tile) -> Bool {
        guard let idx = concealed.firstIndex(of: tile) else { return false }
        concealed.remove(at: idx)
        return true
    }

    /// Move a flower/season from concealed to the bonus area.
    /// No-op if the tile isn't a bonus tile or isn't in concealed.
    @discardableResult
    public mutating func setAsideBonus(_ tile: Tile) -> Bool {
        guard tile.isBonus, let idx = concealed.firstIndex(of: tile) else { return false }
        concealed.remove(at: idx)
        bonus.append(tile)
        return true
    }
}
