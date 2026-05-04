/// Per-pattern scoring weights — base score and multiplier — at level 1.
///
/// Constellations bump these values cumulatively (see `Run.patternBumps`).
/// The numbers come from the design doc's Constellation example
/// "對對 Lv1 = 30 × 2".
public extension Pattern {
    var baseLevel1: Int {
        switch self {
        case .duiDui:   return 30
        case .ping:     return 30
        case .hunYiSe:  return 40
        case .qingYiSe: return 80
        }
    }

    var multLevel1: Double {
        switch self {
        case .duiDui:   return 2.0
        case .ping:     return 2.0
        case .hunYiSe:  return 2.5
        case .qingYiSe: return 4.0
        }
    }
}

/// Cumulative constellation bumps for a single pattern.
public struct PatternBumps: Codable, Sendable, Hashable {
    public var baseDelta: Int = 0
    public var multDelta: Double = 0

    public init(baseDelta: Int = 0, multDelta: Double = 0) {
        self.baseDelta = baseDelta
        self.multDelta = multDelta
    }

    public mutating func apply(base: Int = 0, mult: Double = 0) {
        baseDelta += base
        multDelta += mult
    }
}
