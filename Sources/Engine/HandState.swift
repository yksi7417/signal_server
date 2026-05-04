/// State of a single hand from initial deal to terminal outcome.
///
/// Lifecycle:
/// 1. `HandState.deal(...)` builds the wall, deals each player `handSize`
///    tiles, sets phase to `.awaitingDraw(dealer)`.
/// 2. Player issues `HandAction`s via `apply(_:)`. Each action validates
///    against `legalActions` and either advances the phase or throws.
/// 3. Reaches `.ended` on win or wall exhaustion.
public struct HandState: Codable, Sendable {

    public let config: HandConfig
    public var hands: [Hand]      // [player, ai], indexed by Seat.rawValue
    public var wall: Wall
    public var discards: [DiscardEntry]
    public var phase: Phase
    public var outcome: Outcome?

    public init(
        config: HandConfig,
        hands: [Hand],
        wall: Wall,
        discards: [DiscardEntry] = [],
        phase: Phase,
        outcome: Outcome? = nil
    ) {
        precondition(hands.count == Seat.allCases.count, "hands must have one entry per Seat")
        self.config = config
        self.hands = hands
        self.wall = wall
        self.discards = discards
        self.phase = phase
        self.outcome = outcome
    }

    public func hand(for seat: Seat) -> Hand { hands[seat.rawValue] }

    // MARK: - Phase

    public enum Phase: Codable, Sendable, Hashable {
        case awaitingDraw(Seat)
        case awaitingDiscardOrWin(Seat)
        case awaitingClaim(claimer: Seat, tile: Tile, discarder: Seat)
        case ended
    }

    /// What seat (if any) is "on turn" right now — the one expected to act.
    public var currentSeat: Seat? {
        switch phase {
        case .awaitingDraw(let s):                return s
        case .awaitingDiscardOrWin(let s):        return s
        case .awaitingClaim(let claimer, _, _):   return claimer
        case .ended:                              return nil
        }
    }

    // MARK: - Outcome

    public enum Outcome: Codable, Sendable, Hashable {
        case win(seat: Seat, score: FaanScore, fromDiscard: Seat?)
        case wallExhausted
    }

    // MARK: - Discard log

    public struct DiscardEntry: Codable, Sendable, Hashable {
        public let seat: Seat
        public let tile: Tile
        public init(seat: Seat, tile: Tile) {
            self.seat = seat
            self.tile = tile
        }
    }

    // MARK: - Dealing

    /// Build a fresh `HandState` by shuffling the wall and dealing.
    /// Bonus tiles are auto-set-aside and replaced from the wall.
    public static func deal<G: RandomNumberGenerator>(
        config: HandConfig,
        wallTiles: [Tile],
        dealer: Seat = .player,
        rng: inout G
    ) -> HandState {
        let wall = Wall.shuffled(wallTiles, using: &rng)
        return deal(config: config, wall: wall, dealer: dealer)
    }

    /// Deal from a pre-built (already-ordered) Wall. Useful for deterministic
    /// tests that need exact tile sequences.
    public static func deal(
        config: HandConfig,
        wall startingWall: Wall,
        dealer: Seat = .player
    ) -> HandState {
        var wall = startingWall
        var hands = Seat.allCases.map { _ in Hand() }
        for seat in Seat.allCases {
            let drawn = wall.draw(config.handSize)
            for tile in drawn {
                if tile.isBonus {
                    hands[seat.rawValue].bonus.append(tile)
                } else {
                    hands[seat.rawValue].concealed.append(tile)
                }
            }
            // Replace bonus tiles drawn in the initial deal.
            while hands[seat.rawValue].concealed.count < config.handSize, let extra = wall.draw() {
                if extra.isBonus {
                    hands[seat.rawValue].bonus.append(extra)
                } else {
                    hands[seat.rawValue].concealed.append(extra)
                }
            }
            hands[seat.rawValue].concealed.sort()
        }
        return HandState(
            config: config,
            hands: hands,
            wall: wall,
            phase: .awaitingDraw(dealer)
        )
    }
}
