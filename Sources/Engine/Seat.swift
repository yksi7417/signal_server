/// Two-player seat (MVP). Multi-seat tables come post-MVP per the design doc.
public enum Seat: Int, CaseIterable, Codable, Sendable, Hashable {
    case player = 0
    case ai     = 1

    public var opponent: Seat { self == .player ? .ai : .player }

    /// Player is always East dealer in MVP solo training; AI is South.
    /// Multi-seat play (Phase 3+ of the design doc) reassigns seats.
    public var defaultSeatWind: Wind {
        switch self {
        case .player: return .east
        case .ai:     return .south
        }
    }
}
