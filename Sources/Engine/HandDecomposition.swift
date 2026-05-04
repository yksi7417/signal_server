/// One way to decompose a hand into a pair + sets of three.
///
/// `pair` is the eye; `sets` are pungs/kongs/chows. Bonus tiles (flowers,
/// seasons) are not part of a decomposition — they score separately.
public struct HandDecomposition: Hashable, Sendable {
    public let pair: Tile
    public let sets: [Meld]

    public init(pair: Tile, sets: [Meld]) {
        self.pair = pair
        self.sets = sets
    }

    /// All melds (pair first, then sets).
    public var allMelds: [Meld] {
        [.pair(pair)] + sets
    }
}
