/// A minimal but plausible AI opponent.
///
/// Decision policy:
///   1. If a winning declaration is legal, take it.
///   2. On a claim opportunity, take a winning claim; otherwise pass.
///      (No chow/pong calling for non-winning claims in MVP — see
///       `IMPLEMENTATION_PLAN.md` Phase 10 parking lot.)
///   3. After a draw, discard the tile with the lowest "fitness":
///      isolated tiles go first, paired/sequential tiles are kept.
///
/// Higher-skill AI (shanten-aware, suit-strategy biased) lands post-MVP.
public enum SimpleAI {

    /// Pick an action for `seat` given the current state. Caller is responsible
    /// for ensuring it's actually `seat`'s turn.
    public static func chooseAction<G: RandomNumberGenerator>(
        for seat: Seat,
        in state: HandState,
        rng: inout G
    ) -> HandAction {
        let legal = HandEngine.legalActions(in: state)

        // 1. Take a winning declaration if available.
        for action in legal {
            if case .declareWin = action { return action }
        }

        // 2. Claim opportunity → pass (no chow/pong calling in MVP).
        if case .awaitingClaim = state.phase {
            return .pass(seat)
        }

        // 3. Draw if it's a draw phase.
        if let draw = legal.first(where: { if case .draw = $0 { return true }; return false }) {
            return draw
        }

        // 4. Discard phase: pick the lowest-fitness tile, breaking ties
        //    deterministically using `rng`.
        let hand = state.hand(for: seat).concealed
        guard !hand.isEmpty else {
            // Shouldn't happen in a well-formed state; surface a no-op.
            return .pass(seat)
        }
        let ranked = hand.map { ($0, fitness(of: $0, in: hand)) }
        let minFitness = ranked.map(\.1).min() ?? 0
        let candidates = ranked.filter { $0.1 == minFitness }.map(\.0)
        let pick = candidates[Int.random(in: 0..<candidates.count, using: &rng)]
        return .discard(seat, pick)
    }

    /// Tile "fitness": higher = more useful to keep. Used for discard ranking.
    /// Heuristic-only, not a true shanten count.
    public static func fitness(of tile: Tile, in hand: [Tile]) -> Int {
        var score = 0

        // Duplicate tiles (pair/pung material).
        let dupCount = hand.filter { $0 == tile }.count - 1
        score += dupCount * 3

        // Suited neighbors (chow material, ranks within ±2).
        if let suit = tile.suit, let rank = tile.rank {
            for delta in [-2, -1, 1, 2] {
                let r = rank + delta
                guard r >= 1 && r <= 9 else { continue }
                if hand.contains(.suited(suit, rank: r)) {
                    // Adjacent ranks are more valuable than 2-apart "kanchan".
                    score += abs(delta) == 1 ? 2 : 1
                }
            }
        }

        // Honor tiles get a small standalone bonus — they only need same-tile
        // copies (no chow), so we don't want to over-penalize a single dragon.
        if tile.isHonor && dupCount == 0 {
            score += 1
        }

        return score
    }
}
