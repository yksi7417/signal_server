/// Per-hand rules: hand size, allowed mechanics, win threshold, table context.
///
/// One `HandConfig` is created at the start of each of the 4 hands within a
/// Table. The Run state owns Table progression and produces a `HandConfig`
/// for the current hand.
public struct HandConfig: Hashable, Codable, Sendable {
    public var table: Int             // 1, 2, … (MVP supports 1 and 2)
    public var handIndex: Int         // 1–4 within the Table
    public var prevailingWind: Wind   // East / South / West / North per hand
    public var handSize: Int          // tiles in hand BEFORE the winning draw
                                       // T1 = 4 (win on 5th), T2 = 7 (win on 8th)
    public var minFaanToWin: Int      // 0 for T1, 1 for T2 boss enforcement
    public var allowsChow: Bool       // true from T2 H1 onwards
    public var allowsPong: Bool       // true from T2 H2 onwards
    public var allowsClaimWin: Bool   // win-by-claiming-a-discard
    public var bonusTilesEnabled: Bool // flowers/seasons present in wall
    public var bossModifier: BossModifier?

    public init(
        table: Int,
        handIndex: Int,
        prevailingWind: Wind,
        handSize: Int,
        minFaanToWin: Int = 0,
        allowsChow: Bool = false,
        allowsPong: Bool = false,
        allowsClaimWin: Bool = true,
        bonusTilesEnabled: Bool = false,
        bossModifier: BossModifier? = nil
    ) {
        self.table = table
        self.handIndex = handIndex
        self.prevailingWind = prevailingWind
        self.handSize = handSize
        self.minFaanToWin = minFaanToWin
        self.allowsChow = allowsChow
        self.allowsPong = allowsPong
        self.allowsClaimWin = allowsClaimWin
        self.bonusTilesEnabled = bonusTilesEnabled
        self.bossModifier = bossModifier
    }

    /// True if this is the 4th hand of a Table (the Boss hand).
    public var isBossHand: Bool { handIndex == 4 }
}

/// Boss Wind modifiers that apply only on the 4th hand of a Table.
/// MVP picks 3 from the design-doc parking-lot list.
public enum BossModifier: Codable, Sendable, Hashable {
    /// Whiteout — no calling allowed this hand. Disables claim-win and
    /// any chow/pong calls.
    case whiteout
    /// Frozen Suit — the named suit cannot appear in the final winning hand.
    case frozenSuit(Suit)
    /// Long Night — turn timer added (UI-side) and AI is more aggressive.
    case longNight

    public var displayName: String {
        switch self {
        case .whiteout:        return "Whiteout"
        case .frozenSuit:      return "Frozen Suit"
        case .longNight:       return "Long Night"
        }
    }

    public var description: String {
        switch self {
        case .whiteout:           return "No calling allowed this hand."
        case .frozenSuit(let s):  return "\(s.english) can't be used in your final hand."
        case .longNight:          return "15-second turn timer."
        }
    }

    public var kind: Kind {
        switch self {
        case .whiteout:    return .whiteout
        case .frozenSuit:  return .frozenSuit
        case .longNight:   return .longNight
        }
    }

    public enum Kind: String, CaseIterable, Codable, Sendable, Hashable {
        case whiteout, frozenSuit, longNight
    }
}
