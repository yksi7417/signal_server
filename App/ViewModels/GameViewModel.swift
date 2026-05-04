import SwiftUI
import Engine
import Observation

/// Bridges the headless `Engine` to SwiftUI. Owns the Run + current HandState
/// and drives the AI between human turns.
@Observable
@MainActor
final class GameViewModel {

    // MARK: - State exposed to views
    private(set) var run: Run
    private(set) var handState: HandState
    private(set) var aiThinking: Bool = false
    private(set) var lastError: String?
    private(set) var awaitingNextHand: Bool = false
    private(set) var recentUnlocks: [String] = []

    private var unlockStore = UnlockStore()
    private var aiTickDelay: Duration = .milliseconds(450)

    // MARK: - Init

    init(seed: UInt64? = nil) {
        let resolvedSeed = seed ?? UInt64.random(in: 1...UInt64.max)
        var run = Run(seed: resolvedSeed)
        let state = run.startHand()
        self.run = run
        self.handState = state
        // Kick off the AI loop in case the AI is the dealer for some reason.
        Task { await self.advanceUntilHumanInput() }
    }

    // MARK: - Player intents

    /// Player taps the "draw" button.
    func playerDraw() {
        guard case .awaitingDraw(.player) = handState.phase else { return }
        apply(.draw(.player))
    }

    /// Player taps a tile in their hand to discard it. If the player could
    /// declare a win, prefer the win UI button (`playerDeclareWin`).
    func playerDiscard(_ tile: Tile) {
        guard case .awaitingDiscardOrWin(.player) = handState.phase else { return }
        apply(.discard(.player, tile))
    }

    /// Player declares a win — either self-drawn or claim-on-discard.
    func playerDeclareWin() {
        let legal = HandEngine.legalActions(in: handState)
        if let win = legal.first(where: {
            if case .declareWin(.player, _) = $0 { return true }
            return false
        }) {
            apply(win)
        }
    }

    /// Player passes on a claim opportunity.
    func playerPassClaim() {
        guard case .awaitingClaim(.player, _, _) = handState.phase else { return }
        apply(.pass(.player))
    }

    /// Move past the end-of-hand screen into the next hand (or end of run).
    func continueAfterHand() {
        guard awaitingNextHand else { return }

        let result = handResult(from: handState)
        run.recordHandOutcome(handState)
        let newlyUnlocked = unlockStore.recordHand(result: result, run: run)
        recentUnlocks = newlyUnlocked.map { "\($0.kind.rawValue): \($0.id)" }

        awaitingNextHand = false
        if run.status != .inProgress {
            // Run complete — leave state so the outcome screen can show the totals.
            return
        }
        handState = run.startHand()
        Task { await self.advanceUntilHumanInput() }
    }

    // MARK: - Computed view helpers

    var canDeclareWin: Bool {
        HandEngine.legalActions(in: handState).contains(where: {
            if case .declareWin(.player, _) = $0 { return true }
            return false
        })
    }

    var isPlayersTurn: Bool { handState.currentSeat == .player }

    var isAwaitingPlayerClaim: Bool {
        if case .awaitingClaim(.player, _, _) = handState.phase { return true }
        return false
    }

    var isAwaitingPlayerDraw: Bool {
        if case .awaitingDraw(.player) = handState.phase { return true }
        return false
    }

    var isAwaitingPlayerDiscard: Bool {
        if case .awaitingDiscardOrWin(.player) = handState.phase { return true }
        return false
    }

    var pendingClaimTile: Tile? {
        if case .awaitingClaim(.player, let tile, _) = handState.phase { return tile }
        return nil
    }

    // MARK: - Result extraction

    private func handResult(from state: HandState) -> HandResult {
        var won = false
        var primaryPattern: Pattern?
        var score = 0
        if case .win(let seat, let faanScore, _) = state.outcome, seat == .player {
            won = true
            score = faanScore.faan
            // Pick the highest-faan pattern as the "primary" for unlock keying.
            for reason in faanScore.reasons {
                for p in Pattern.allCases where p.chinese == reason.label {
                    primaryPattern = p
                }
            }
        }
        let discards = state.discards.filter { $0.seat == .player }.count
        return HandResult(
            playerWon: won,
            primaryPattern: primaryPattern,
            score: score,
            discardsThisHand: discards,
            spellsUsedThisHand: 0   // Spells UI not wired yet — Phase 9 polish
        )
    }

    // MARK: - Internal driver

    private func apply(_ action: HandAction) {
        do {
            try HandEngine.apply(action, to: &handState)
            lastError = nil
        } catch {
            lastError = "\(error)"
            return
        }
        if handState.phase == .ended {
            awaitingNextHand = true
            return
        }
        Task { await self.advanceUntilHumanInput() }
    }

    private func advanceUntilHumanInput() async {
        // Loop applying AI actions until it's the player's turn or the hand ends.
        while handState.phase != .ended {
            guard let seat = handState.currentSeat else { break }
            if seat == .player { return }

            aiThinking = true
            try? await Task.sleep(for: aiTickDelay)
            aiThinking = false

            let action = SimpleAI.chooseAction(for: .ai, in: handState, rng: &run.rng)
            do {
                try HandEngine.apply(action, to: &handState)
            } catch {
                lastError = "\(error)"
                return
            }
        }
        if handState.phase == .ended {
            awaitingNextHand = true
        }
    }
}
