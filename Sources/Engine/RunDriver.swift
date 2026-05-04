/// Runs a single hand to terminal state using a player strategy and the
/// `SimpleAI` for the AI seat. Useful for headless simulation (CLI),
/// integration tests, and as a reference flow for the iOS app.
public enum RunDriver {

    /// A `Strategy` decides what action to take for a given seat in a state.
    /// Default strategy delegates to `SimpleAI`. The iOS app would supply a
    /// human-driven strategy that suspends until the user taps.
    public typealias Strategy = (Seat, HandState) -> HandAction

    public static func defaultStrategy<G: RandomNumberGenerator>(rng: inout G) -> Strategy {
        // Capture the RNG by reference via a closure-bound generator.
        // Since RandomNumberGenerator is a protocol and `inout` cannot be
        // captured, copy the state out for use inside the closure.
        var rngState = rng
        let strategy: Strategy = { seat, state in
            SimpleAI.chooseAction(for: seat, in: state, rng: &rngState)
        }
        // Note: callers that need RNG continuity across hands should pass
        // their own strategy that mutates a shared RNG.
        return strategy
    }

    /// Play `state` until it reaches `.ended`. Mutates state in place.
    /// `strategy` chooses actions for both seats; for solo training the iOS
    /// app uses the human driver for `.player` and `SimpleAI` for `.ai`.
    @discardableResult
    public static func playHand(
        state: inout HandState,
        strategy: Strategy
    ) throws -> Int {
        var iterations = 0
        let safetyLimit = 1_000   // detect runaway loops
        while state.phase != .ended {
            iterations += 1
            if iterations > safetyLimit {
                throw RunDriverError.runawayLoop(iterations: iterations)
            }
            guard let seat = state.currentSeat else { break }
            let action = strategy(seat, state)
            try HandEngine.apply(action, to: &state)
        }
        return iterations
    }

    /// Play hand using `SimpleAI` for both seats, with a shared RNG.
    public static func playHandWithSimpleAI<G: RandomNumberGenerator>(
        state: inout HandState,
        rng: inout G
    ) throws -> Int {
        var localRNG = rng
        defer { rng = localRNG }
        return try playHand(state: &state) { seat, st in
            SimpleAI.chooseAction(for: seat, in: st, rng: &localRNG)
        }
    }
}

public enum RunDriverError: Error, Sendable, Hashable {
    case runawayLoop(iterations: Int)
}
