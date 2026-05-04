/// A single mahjong tile.
///
/// Suited ranks are 1–9. Flowers and seasons are indexed 1–4 and pair with
/// the matching seat wind (1=East, 2=South, 3=West, 4=North) for a +1 faan
/// bonus when held by that seat. The joker case represents an in-tile wild
/// (unlocked at Table 3+; never present in the standard wall, only added
/// via spell or higher-Table setup).
public enum Tile: Hashable, Codable, Sendable {
    case suited(Suit, rank: Int)
    case wind(Wind)
    case dragon(Dragon)
    case flower(Int)  // 1-4
    case season(Int)  // 1-4
    case joker

    public var isSuited: Bool {
        if case .suited = self { return true }
        return false
    }

    public var isHonor: Bool {
        switch self {
        case .wind, .dragon: return true
        default:             return false
        }
    }

    public var isBonus: Bool {
        switch self {
        case .flower, .season: return true
        default:               return false
        }
    }

    public var isJoker: Bool {
        if case .joker = self { return true }
        return false
    }

    /// Suit if this is a suited tile, else nil.
    public var suit: Suit? {
        if case let .suited(suit, _) = self { return suit }
        return nil
    }

    /// Rank 1–9 if this is a suited tile, else nil.
    public var rank: Int? {
        if case let .suited(_, rank) = self { return rank }
        return nil
    }
}

extension Tile: CustomStringConvertible {
    public var description: String {
        switch self {
        case .suited(let suit, let rank): return "\(rank)\(suit.chinese)"
        case .wind(let wind):             return wind.chinese
        case .dragon(let dragon):         return dragon.chinese
        case .flower(let n):              return "F\(n)"
        case .season(let n):              return "S\(n)"
        case .joker:                      return "J"
        }
    }
}
