extension Tile {
    /// Canonical ordering used by the validator and UI:
    /// Cookies 1–9, Bamboo 1–9, Characters 1–9, Winds (E,S,W,N),
    /// Dragons (R,G,W), Flowers 1–4, Seasons 1–4, Joker.
    public var sortIndex: Int {
        switch self {
        case .suited(.cookies, let r):    return  0 + r       //  1– 9
        case .suited(.bamboo, let r):     return 10 + r       // 11–19
        case .suited(.characters, let r): return 20 + r       // 21–29
        case .wind(.east):                return 31
        case .wind(.south):               return 32
        case .wind(.west):                return 33
        case .wind(.north):               return 34
        case .dragon(.red):               return 41
        case .dragon(.green):             return 42
        case .dragon(.white):             return 43
        case .flower(let n):              return 50 + n
        case .season(let n):              return 60 + n
        case .joker:                      return 99
        }
    }
}

extension Tile: Comparable {
    public static func < (lhs: Tile, rhs: Tile) -> Bool {
        lhs.sortIndex < rhs.sortIndex
    }
}
