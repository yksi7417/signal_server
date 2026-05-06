import SwiftUI
import Engine
import Observation

/// Bridges the headless `Engine` to SwiftUI. Owns the Run, current HandState,
/// shop offers, and unlock progression. Drives the AI between human turns.
@Observable
@MainActor
final class GameViewModel {

    // MARK: - State exposed to views
    private(set) var run: Run
    private(set) var handState: HandState
    private(set) var aiThinking: Bool = false
    private(set) var lastError: String?
    private(set) var awaitingNextHand: Bool = false
    private(set) var awaitingShop: Bool = false
    private(set) var shop: Shop?
    private(set) var openedPack: PackContents?
    private(set) var openedPackChoices: Int = 0
    private(set) var unlockStore = UnlockStore()
    private(set) var recentUnlocks: [String] = []

    /// In-progress tile-swap spell: nil unless the player tapped a Swap
    /// consumable. Tracks which hand tile is selected (if any).
    private(set) var pendingSwap: PendingSwap?

    private var aiTickDelay: Duration = .milliseconds(450)

    // MARK: - Init

    init(seed: UInt64? = nil, tutorial: Bool = true) {
        let resolvedSeed = seed ?? UInt64.random(in: 1...UInt64.max)
        var run = Run(seed: resolvedSeed, tutorial: tutorial)
        let state = run.startHand()
        self.run = run
        self.handState = state
        Task { await self.advanceUntilHumanInput() }
    }

    // MARK: - Tile-swap spell flow

    struct PendingSwap: Equatable {
        var consumableId: String
        var selectedHandTile: Tile?
    }

    /// Player tapped a Swap consumable. Enters tile-pick mode.
    func beginTileSwap(consumableId: String) {
        guard run.consumables.contains(where: { $0.id == consumableId }) else { return }
        pendingSwap = PendingSwap(consumableId: consumableId, selectedHandTile: nil)
    }

    /// Cancel an in-flight swap (e.g. user tapped the X).
    func cancelTileSwap() {
        pendingSwap = nil
    }

    /// During the swap flow, tapping a hand tile selects it as the source.
    func swapPickHandTile(_ tile: Tile) {
        guard pendingSwap != nil else { return }
        pendingSwap?.selectedHandTile = tile
    }

    /// During the swap flow, tapping a wall tile commits the swap.
    func swapCommit(wallRelativeIndex: Int) {
        guard let pending = pendingSwap, let handTile = pending.selectedHandTile else { return }
        let ok = run.applySwap(
            handTile: handTile,
            wallRelativeIndex: wallRelativeIndex,
            seat: .player,
            in: &handState
        )
        if !ok {
            lastError = "Couldn't swap that tile"
        }
        pendingSwap = nil
    }

    /// Returns the array of undrawn wall tiles for the swap picker UI.
    var wallUndrawn: [Tile] { Array(handState.wall.undrawn) }

    /// Whether to render the AI's hand face up.
    var revealOpponentHand: Bool { run.revealsOpponentHand }

    // MARK: - Player intents (gameplay)

    func playerDraw() {
        guard case .awaitingDraw(.player) = handState.phase else { return }
        apply(.draw(.player))
    }

    func playerDiscard(_ tile: Tile) {
        guard case .awaitingDiscardOrWin(.player) = handState.phase else { return }
        apply(.discard(.player, tile))
    }

    func playerDeclareWin() {
        let legal = HandEngine.legalActions(in: handState)
        if let win = legal.first(where: {
            if case .declareWin(.player, _) = $0 { return true }
            return false
        }) {
            apply(win)
        }
    }

    func playerPassClaim() {
        guard case .awaitingClaim(.player, _, _) = handState.phase else { return }
        apply(.pass(.player))
    }

    /// User dismisses the per-hand outcome card. Records outcome, advances run.
    /// If run is still in progress and we have coins to spend, opens the shop.
    /// Otherwise starts the next hand directly.
    func continueAfterHand() {
        guard awaitingNextHand else { return }

        let result = handResult(from: handState)
        run.recordHandOutcome(handState)
        let newlyUnlocked = unlockStore.recordHand(result: result, run: run)
        recentUnlocks = newlyUnlocked.map { displayName(for: $0) }

        awaitingNextHand = false
        if run.status != .inProgress {
            // Run ended — leave the outcome screen up; UI shows summary.
            return
        }
        openShop()
    }

    /// Called from the run-complete screen — start a new run.
    func startNewRun(tutorial: Bool = true) {
        let newSeed = UInt64.random(in: 1...UInt64.max)
        var fresh = Run(seed: newSeed, tutorial: tutorial)
        let state = fresh.startHand()
        self.run = fresh
        self.handState = state
        self.recentUnlocks = []
        self.shop = nil
        self.openedPack = nil
        self.awaitingNextHand = false
        self.awaitingShop = false
        self.pendingSwap = nil
        Task { await self.advanceUntilHumanInput() }
    }

    // MARK: - Shop

    private func openShop() {
        let offer = ShopRoller.rollShop(
            unlocked: unlockStore.pool,
            currentTable: run.table,
            rng: &run.rng
        )
        self.shop = offer
        self.awaitingShop = true
    }

    func closeShop() {
        guard awaitingShop else { return }
        awaitingShop = false
        shop = nil
        openedPack = nil
        // Now actually deal the next hand.
        handState = run.startHand()
        Task { await self.advanceUntilHumanInput() }
    }

    func buyCharm(_ shopCharm: ShopCharm) {
        guard awaitingShop, var current = shop else { return }
        guard run.coins >= shopCharm.price, run.canAddCharm else {
            lastError = run.coins < shopCharm.price ? "Not enough coins" : "Charm slots full"
            return
        }
        let added = run.addCharm(shopCharm.charm)
        guard added else {
            lastError = "Couldn't add charm"
            return
        }
        run.coins -= shopCharm.price
        // Remove the bought charm from the offer.
        current.charms.removeAll(where: { $0.id == shopCharm.id })
        self.shop = current
        lastError = nil
    }

    func reroll() {
        guard awaitingShop, var current = shop else { return }
        guard run.coins >= current.rerollCost else {
            lastError = "Not enough coins to reroll"
            return
        }
        run.coins -= current.rerollCost
        let nextRolls = current.rerollsUsed + 1
        let fresh = ShopRoller.rollShop(
            unlocked: unlockStore.pool,
            currentTable: run.table,
            rng: &run.rng,
            rerollsUsed: nextRolls
        )
        self.shop = fresh
        lastError = nil
    }

    func buyPack() {
        guard awaitingShop, let current = shop else { return }
        guard run.coins >= current.pack.price else {
            lastError = "Not enough coins for pack"
            return
        }
        run.coins -= current.pack.price
        let contents = ShopRoller.openPack(
            current.pack,
            unlocked: unlockStore.pool,
            currentTable: run.table,
            rng: &run.rng
        )
        self.openedPack = contents
        self.openedPackChoices = 0
        lastError = nil
    }

    /// Pick one item from the currently-opened pack. Decrements pickCount.
    func pickFromPack(_ kind: PackPickKind) {
        guard var pack = openedPack else { return }
        switch kind {
        case .charm(let c):
            if run.canAddCharm, run.addCharm(c) {
                pack.charms.removeAll { $0.id == c.id }
                openedPackChoices += 1
            } else {
                lastError = "Charm slots full or duplicate"
            }
        case .constellation(let c):
            if run.canAddConsumable, run.addConsumable(.constellation(c)) {
                pack.constellations.removeAll { $0.id == c.id }
                openedPackChoices += 1
            } else {
                lastError = "Consumable slots full"
            }
        case .spell(let s):
            if run.canAddConsumable, run.addConsumable(.spell(s)) {
                pack.spells.removeAll { $0.id == s.id }
                openedPackChoices += 1
            } else {
                lastError = "Consumable slots full"
            }
        }
        if openedPackChoices >= pack.pickCount {
            // Done picking; close the pack.
            self.openedPack = nil
            self.openedPackChoices = 0
        } else {
            self.openedPack = pack
        }
    }

    func skipPack() {
        openedPack = nil
        openedPackChoices = 0
    }

    enum PackPickKind {
        case charm(Charm)
        case constellation(Constellation)
        case spell(Spell)
    }

    // MARK: - Consumables (in-hand use)

    func useConsumable(id: String) {
        // Tile Swap is the only mid-hand spell wired through the engine today;
        // route it into the swap-picker flow regardless of phase.
        if let consumable = run.consumables.first(where: { $0.id == id }),
           case .spell(let s) = consumable, s.effect == .swapWithWall {
            beginTileSwap(consumableId: id)
            return
        }
        // Other spells / constellations: between-hand only for now.
        guard awaitingShop || awaitingNextHand else {
            lastError = "Spells/constellations are between-hand only for now"
            return
        }
        if run.useConsumable(id: id) {
            lastError = nil
        }
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
    var runEnded: Bool { run.status != .inProgress }

    // MARK: - Result extraction

    private func handResult(from state: HandState) -> HandResult {
        var won = false
        var primaryPattern: Pattern?
        var score = 0
        if case .win(let seat, let faanScore, _) = state.outcome, seat == .player {
            won = true
            score = faanScore.faan
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
            spellsUsedThisHand: 0
        )
    }

    private func displayName(for unlock: Unlock) -> String {
        switch unlock.kind {
        case .charm:
            return CharmCatalog.starter.first(where: { $0.id == unlock.id })?.name ?? unlock.id
        case .constellation:
            return ConstellationCatalog.starter.first(where: { $0.id == unlock.id })?.name ?? unlock.id
        case .spell:
            return SpellCatalog.starter.first(where: { $0.id == unlock.id })?.name ?? unlock.id
        }
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
