/// The draw pile for a single hand. Pre-shuffled at construction; tiles are
/// drawn one at a time from the front. Encodable for save/restore mid-hand.
public struct Wall: Hashable, Codable, Sendable {
    public private(set) var tiles: [Tile]
    public private(set) var drawIndex: Int

    public init(tiles: [Tile]) {
        self.tiles = tiles
        self.drawIndex = 0
    }

    /// Build a wall by shuffling `tiles` with the given RNG. Use a
    /// `SeededRandomNumberGenerator` for reproducible deals.
    public static func shuffled<G: RandomNumberGenerator>(
        _ tiles: [Tile],
        using rng: inout G
    ) -> Wall {
        var copy = tiles
        copy.shuffle(using: &rng)
        return Wall(tiles: copy)
    }

    public var remaining: Int { tiles.count - drawIndex }
    public var isEmpty: Bool { remaining == 0 }

    /// Draws the next tile, or nil if the wall is exhausted.
    public mutating func draw() -> Tile? {
        guard drawIndex < tiles.count else { return nil }
        let tile = tiles[drawIndex]
        drawIndex += 1
        return tile
    }

    /// Returns the next `n` tiles without advancing. Useful for dealing.
    public func peek(_ n: Int) -> [Tile] {
        Array(tiles[drawIndex ..< min(drawIndex + n, tiles.count)])
    }

    /// Bulk-draws `n` tiles. If the wall has fewer than `n` left, returns
    /// what remains and leaves the wall empty.
    public mutating func draw(_ n: Int) -> [Tile] {
        var out: [Tile] = []
        out.reserveCapacity(n)
        for _ in 0..<n {
            if let t = draw() { out.append(t) } else { break }
        }
        return out
    }
}
