/// Winning patterns the MVP scorer recognizes.
///
/// Patterns aren't always mutually exclusive — e.g. a hand can be both
/// 對對 (all pungs) and 清一色 (pure one suit). Scoring sums their faan
/// where the design doc treats them as additive; mutually-exclusive cases
/// (混一色 vs 清一色) are resolved in `FaanCalculator`.
public enum Pattern: String, CaseIterable, Codable, Sendable, Hashable {
    /// 對對 Dui Dui — all sets are pungs/kongs (no chows).
    case duiDui
    /// 平 Ping — all sets are chows AND in a single number suit (no honors).
    case ping
    /// 混一色 Hun Yi Se — exactly one number suit + honor tiles.
    case hunYiSe
    /// 清一色 Qing Yi Se — pure one number suit, no honors.
    case qingYiSe

    public var chinese: String {
        switch self {
        case .duiDui:   return "對對"
        case .ping:     return "平"
        case .hunYiSe:  return "混一色"
        case .qingYiSe: return "清一色"
        }
    }

    public var english: String {
        switch self {
        case .duiDui:   return "All Pungs"
        case .ping:     return "All Sequences"
        case .hunYiSe:  return "Mixed One Suit"
        case .qingYiSe: return "Pure One Suit"
        }
    }
}
