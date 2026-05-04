/// Actions that drive a `HandState` forward. Each action targets a specific
/// seat and is validated against the current phase before being applied.
public enum HandAction: Codable, Sendable, Hashable {
    /// Draw the next tile from the wall.
    case draw(Seat)
    /// Discard a tile from the seat's concealed hand.
    case discard(Seat, Tile)
    /// Declare a winning hand. `fromDiscard` = true means this is a claim-win
    /// on an opponent's just-discarded tile; false means self-drawn.
    case declareWin(Seat, fromDiscard: Bool)
    /// Pass on the current claim opportunity.
    case pass(Seat)
}

public enum HandActionError: Error, Hashable, Sendable {
    case wrongTurn(expected: Seat?, got: Seat)
    case wrongPhase
    case tileNotInHand(Tile)
    case wallExhausted
    case notWinning
    case faanBelowMinimum(faan: Int, required: Int)
    case callingDisabled
}
