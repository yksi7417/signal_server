/// Action validator + applier for a single hand. All mutation goes through
/// `HandEngine.apply(action:to:)`; never mutate `HandState` ad-hoc from
/// outside this file.
public enum HandEngine {

    /// All actions currently legal for the given state. Drivers (UI / AI)
    /// should pick exclusively from this list.
    public static func legalActions(in state: HandState) -> [HandAction] {
        switch state.phase {
        case .awaitingDraw(let seat):
            return state.wall.isEmpty ? [] : [.draw(seat)]

        case .awaitingDiscardOrWin(let seat):
            var actions: [HandAction] = []
            // Win check (self-drawn) — concealed already includes the drawn tile.
            if isWinningWithFaan(state: state, seat: seat, fromDiscard: false) {
                actions.append(.declareWin(seat, fromDiscard: false))
            }
            for tile in state.hand(for: seat).concealed {
                actions.append(.discard(seat, tile))
            }
            return actions

        case .awaitingClaim(let claimer, let tile, _):
            var actions: [HandAction] = [.pass(claimer)]
            if state.config.allowsClaimWin && !whiteoutBlocksCalling(state: state) {
                if canClaimWin(state: state, claimer: claimer, tile: tile) {
                    actions.append(.declareWin(claimer, fromDiscard: true))
                }
            }
            return actions

        case .ended:
            return []
        }
    }

    /// Apply an action, mutating `state`. Throws if the action is illegal.
    public static func apply(_ action: HandAction, to state: inout HandState) throws {
        switch action {
        case .draw(let seat):
            try expectPhase(state, .awaitingDraw(seat))
            guard let tile = state.wall.draw() else {
                state.phase = .ended
                state.outcome = .wallExhausted
                throw HandActionError.wallExhausted
            }
            // Auto-set-aside any bonus tile and immediately replacement-draw.
            if tile.isBonus {
                state.hands[seat.rawValue].bonus.append(tile)
                // Replacement draw — recurse.
                state.phase = .awaitingDraw(seat)
                try apply(.draw(seat), to: &state)
                return
            }
            state.hands[seat.rawValue].concealed.append(tile)
            state.hands[seat.rawValue].concealed.sort()
            state.phase = .awaitingDiscardOrWin(seat)

        case .discard(let seat, let tile):
            try expectPhase(state, .awaitingDiscardOrWin(seat))
            guard state.hands[seat.rawValue].discard(tile) else {
                throw HandActionError.tileNotInHand(tile)
            }
            state.discards.append(.init(seat: seat, tile: tile))

            // Hand off to claim phase if opponent might want it; else pass turn.
            let opponent = seat.opponent
            if shouldOfferClaim(state: state, claimer: opponent, tile: tile) {
                state.phase = .awaitingClaim(claimer: opponent, tile: tile, discarder: seat)
            } else {
                transitionToDrawOrEnd(state: &state, seat: opponent)
            }

        case .declareWin(let seat, let fromDiscard):
            if fromDiscard {
                guard case .awaitingClaim(let claimer, let tile, let discarder) = state.phase,
                      claimer == seat else {
                    throw HandActionError.wrongPhase
                }
                if !state.config.allowsClaimWin || whiteoutBlocksCalling(state: state) {
                    throw HandActionError.callingDisabled
                }
                // Add the claimed tile to the hand and validate.
                state.hands[seat.rawValue].concealed.append(tile)
                state.hands[seat.rawValue].concealed.sort()
                guard HandValidator.isWinning(state.hand(for: seat)) else {
                    // Roll back and surface error.
                    _ = state.hands[seat.rawValue].discard(tile)
                    throw HandActionError.notWinning
                }
                let score = computeScore(state: state, seat: seat, selfDrawn: false)
                if score.faan < state.config.minFaanToWin {
                    _ = state.hands[seat.rawValue].discard(tile)
                    throw HandActionError.faanBelowMinimum(faan: score.faan, required: state.config.minFaanToWin)
                }
                state.phase = .ended
                state.outcome = .win(seat: seat, score: score, fromDiscard: discarder)

            } else {
                try expectPhase(state, .awaitingDiscardOrWin(seat))
                let h = state.hand(for: seat)
                guard HandValidator.isWinning(h) else {
                    throw HandActionError.notWinning
                }
                if frozenSuitBlocksWin(state: state, hand: h) {
                    throw HandActionError.notWinning
                }
                let score = computeScore(state: state, seat: seat, selfDrawn: true)
                if score.faan < state.config.minFaanToWin {
                    throw HandActionError.faanBelowMinimum(faan: score.faan, required: state.config.minFaanToWin)
                }
                state.phase = .ended
                state.outcome = .win(seat: seat, score: score, fromDiscard: nil)
            }

        case .pass(let seat):
            guard case .awaitingClaim(let claimer, _, let discarder) = state.phase,
                  claimer == seat else {
                throw HandActionError.wrongPhase
            }
            // Turn moves to the claimer (who just passed).
            _ = discarder
            transitionToDrawOrEnd(state: &state, seat: claimer)
        }
    }

    /// Move to `awaitingDraw` if the wall has tiles, otherwise terminate the
    /// hand as `.wallExhausted`. Centralizes the "is the wall empty?" check
    /// that follows every discard/claim-pass.
    private static func transitionToDrawOrEnd(state: inout HandState, seat: Seat) {
        if state.wall.isEmpty {
            state.phase = .ended
            state.outcome = .wallExhausted
        } else {
            state.phase = .awaitingDraw(seat)
        }
    }

    // MARK: - Helpers

    private static func expectPhase(_ state: HandState, _ expected: HandState.Phase) throws {
        if state.phase != expected {
            throw HandActionError.wrongPhase
        }
    }

    /// Should we offer the opponent a claim opportunity on this discard?
    /// MVP: only if claim-win is allowed *and* claiming would actually win.
    private static func shouldOfferClaim(state: HandState, claimer: Seat, tile: Tile) -> Bool {
        guard state.config.allowsClaimWin else { return false }
        guard !whiteoutBlocksCalling(state: state) else { return false }
        return canClaimWin(state: state, claimer: claimer, tile: tile)
    }

    private static func canClaimWin(state: HandState, claimer: Seat, tile: Tile) -> Bool {
        var probe = state.hand(for: claimer)
        probe.concealed.append(tile)
        guard HandValidator.isWinning(probe) else { return false }
        if frozenSuitBlocksWin(state: state, hand: probe) { return false }
        let score = scoreProbe(state: state, hand: probe, seat: claimer, selfDrawn: false)
        return score.faan >= state.config.minFaanToWin
    }

    /// Boss modifier convenience — Whiteout disables all calling.
    private static func whiteoutBlocksCalling(state: HandState) -> Bool {
        if case .whiteout = state.config.bossModifier { return true }
        return false
    }

    /// Frozen-suit constraint — a winning hand can't include the named suit.
    private static func frozenSuitBlocksWin(state: HandState, hand: Hand) -> Bool {
        if case .frozenSuit(let frozen) = state.config.bossModifier {
            return hand.playTiles.contains(where: { $0.suit == frozen })
        }
        return false
    }

    /// Score a real (post-mutation) hand attached to a seat.
    private static func computeScore(state: HandState, seat: Seat, selfDrawn: Bool) -> FaanScore {
        let ctx = ScoringContext(seatWind: seat.defaultSeatWind, selfDrawn: selfDrawn)
        return FaanCalculator.score(hand: state.hand(for: seat), context: ctx)
    }

    private static func scoreProbe(state: HandState, hand: Hand, seat: Seat, selfDrawn: Bool) -> FaanScore {
        let ctx = ScoringContext(seatWind: seat.defaultSeatWind, selfDrawn: selfDrawn)
        return FaanCalculator.score(hand: hand, context: ctx)
    }

    /// True if `seat` could declare a winning hand right now (used for legal-action probing).
    public static func isWinningWithFaan(state: HandState, seat: Seat, fromDiscard: Bool) -> Bool {
        let hand = state.hand(for: seat)
        guard HandValidator.isWinning(hand) else { return false }
        if frozenSuitBlocksWin(state: state, hand: hand) { return false }
        let score = scoreProbe(state: state, hand: hand, seat: seat, selfDrawn: !fromDiscard)
        return score.faan >= state.config.minFaanToWin
    }
}
