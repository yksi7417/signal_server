/// A meld is a structured group of tiles: pair, pung, kong, or chow.
///
/// - `pair`: 2 identical tiles (only ever the "eye" of a winning hand)
/// - `pung`: 3 identical tiles
/// - `kong`: 4 identical tiles. `exposed = false` for concealed kongs.
/// - `chow`: 3 sequential ranks of the same suit. Stored as suit + low rank;
///   represents low, low+1, low+2.
public enum Meld: Hashable, Codable, Sendable {
    case pair(Tile)
    case pung(Tile)
    case kong(Tile, exposed: Bool)
    case chow(Suit, low: Int)

    /// The constituent tiles, in canonical order.
    public var tiles: [Tile] {
        switch self {
        case .pair(let t):       return [t, t]
        case .pung(let t):       return [t, t, t]
        case .kong(let t, _):    return [t, t, t, t]
        case .chow(let s, let l): return (0..<3).map { .suited(s, rank: l + $0) }
        }
    }

    public var isPair: Bool { if case .pair = self { return true }; return false }
    public var isPung: Bool { if case .pung = self { return true }; return false }
    public var isKong: Bool { if case .kong = self { return true }; return false }
    public var isChow: Bool { if case .chow = self { return true }; return false }

    /// True for melds that count as a "set" of three (or kong's 4 collapsed
    /// to one set) — i.e. anything except a pair.
    public var isSet: Bool { !isPair }

    /// Honor melds (winds/dragons) — only ever pair/pung/kong, never chow.
    public var isHonorMeld: Bool {
        switch self {
        case .pair(let t), .pung(let t), .kong(let t, _): return t.isHonor
        case .chow:                                       return false
        }
    }

    /// The single suit this meld lives in, if it's a numbered (suited) meld.
    /// Returns nil for honor melds and bonus tiles.
    public var suit: Suit? {
        switch self {
        case .pair(let t), .pung(let t), .kong(let t, _): return t.suit
        case .chow(let s, _):                             return s
        }
    }
}
