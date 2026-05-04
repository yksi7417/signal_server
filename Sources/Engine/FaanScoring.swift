/// A single labeled contribution to a hand's faan total.
public struct FaanReason: Hashable, Codable, Sendable {
    public let label: String
    public let faan: Int

    public init(label: String, faan: Int) {
        self.label = label
        self.faan = faan
    }
}

/// Maps a flower/season index (1–4) to the seat wind it pairs with.
/// 1=East, 2=South, 3=West, 4=North per traditional convention.
public func seatWind(forBonusIndex n: Int) -> Wind? {
    switch n {
    case 1: return .east
    case 2: return .south
    case 3: return .west
    case 4: return .north
    default: return nil
    }
}

/// Per-hand context passed to the scorer: who is the winner, was it self-drawn?
public struct ScoringContext: Sendable {
    public var seatWind: Wind
    public var selfDrawn: Bool

    public init(seatWind: Wind, selfDrawn: Bool) {
        self.seatWind = seatWind
        self.selfDrawn = selfDrawn
    }
}

/// Computed score for a single winning hand.
public struct FaanScore: Hashable, Codable, Sendable {
    public let faan: Int
    public let reasons: [FaanReason]

    public init(faan: Int, reasons: [FaanReason]) {
        self.faan = faan
        self.reasons = reasons
    }
}

/// MVP faan scorer — implements the table from the design doc:
///
/// | Pattern                                  | Faan |
/// |------------------------------------------|------|
/// | 平 (all sequences, one suit)             | 1    |
/// | 對對 (all pairs/pungs)                   | 1    |
/// | 混一色 (one suit + honors)               | 2    |
/// | 清一色 (pure one suit)                   | 4    |
/// | Flower/Season matching seat wind         | +1   |
/// | Self-drawn winning tile                  | +1   |
public enum FaanCalculator {

    /// Faan value for a single pattern.
    public static func faan(for pattern: Pattern) -> Int {
        switch pattern {
        case .ping:     return 1
        case .duiDui:   return 1
        case .hunYiSe:  return 2
        case .qingYiSe: return 4
        }
    }

    /// Score a winning hand. If the hand is not winning, returns `(0, [])`.
    public static func score(hand: Hand, context: ScoringContext) -> FaanScore {
        guard HandValidator.isWinning(hand) else {
            return FaanScore(faan: 0, reasons: [])
        }

        var reasons: [FaanReason] = []
        let patterns = PatternDetector.patterns(in: hand)

        // 清一色 and 混一色 are mutually exclusive — keep only the higher.
        var effective = patterns
        if effective.contains(.qingYiSe) {
            effective.remove(.hunYiSe)
        }

        // Pattern faan, in canonical order for stable breakdown.
        let order: [Pattern] = [.ping, .duiDui, .hunYiSe, .qingYiSe]
        for p in order where effective.contains(p) {
            reasons.append(FaanReason(label: p.chinese, faan: faan(for: p)))
        }

        // Bonus tiles matching seat wind.
        for tile in hand.bonus {
            switch tile {
            case .flower(let n):
                if seatWind(forBonusIndex: n) == context.seatWind {
                    reasons.append(FaanReason(label: "Flower-\(context.seatWind.english)", faan: 1))
                }
            case .season(let n):
                if seatWind(forBonusIndex: n) == context.seatWind {
                    reasons.append(FaanReason(label: "Season-\(context.seatWind.english)", faan: 1))
                }
            default: break
            }
        }

        // Self-drawn bonus.
        if context.selfDrawn {
            reasons.append(FaanReason(label: "Self-Drawn", faan: 1))
        }

        let total = reasons.reduce(0) { $0 + $1.faan }
        return FaanScore(faan: total, reasons: reasons)
    }
}

/// Coin payout from a faan score.
public enum CoinCalculator {

    /// Base coins per faan point.
    public static let basePerFaan = 5

    /// Bonus for clearing a full Table without losing a hand.
    public static let tableSweepBonus = 20

    /// Coin payout for a single-hand win.
    public static func coins(for score: FaanScore) -> Int {
        max(0, score.faan) * basePerFaan
    }

    /// Total coins for clearing a Table (4 hands), with optional sweep bonus
    /// when none of the 4 hands were lost.
    public static func tableCompletionBonus(swept: Bool) -> Int {
        swept ? tableSweepBonus : 0
    }
}
