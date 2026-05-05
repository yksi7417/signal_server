import SwiftUI
import Engine

/// Main gameplay screen — opponent at top, discard pool in middle, player's
/// hand and action buttons at bottom.
struct GameView: View {
    @State private var vm: GameViewModel
    @Environment(\.dismiss) private var dismiss

    init(seed: UInt64? = nil) {
        _vm = State(initialValue: GameViewModel(seed: seed))
    }

    var body: some View {
        ZStack {
            Theme.lanai.ignoresSafeArea()

            VStack(spacing: 0) {
                RunStatusView(
                    table: vm.run.table,
                    handIndex: vm.run.handIndex,
                    prevailingWind: vm.handState.config.prevailingWind,
                    coins: vm.run.coins,
                    bossModifier: vm.handState.config.bossModifier
                )
                ActiveInventoryView(
                    charms: vm.run.charms,
                    consumables: vm.run.consumables,
                    onUseConsumable: { id in vm.useConsumable(id: id) }
                )
                Divider().background(Theme.gold.opacity(0.4))

                opponentRow
                    .padding(.top, 16)

                Spacer(minLength: 12)

                DiscardPileView(entries: vm.handState.discards)
                    .padding(.horizontal, 16)

                Spacer(minLength: 12)

                playerRow
                    .padding(.bottom, 16)

                actionBar
                    .padding(.horizontal, 16)
                    .padding(.bottom, 24)
            }
        }
        .overlay(alignment: .top) { errorBanner }
        .overlay { handEndedOverlay }
        .overlay { shopOverlay }
        .overlay { runCompleteOverlay }
    }

    // MARK: - Opponent

    private var opponentRow: some View {
        VStack(spacing: 6) {
            HStack(spacing: 8) {
                Text("AI · \(vm.handState.hand(for: .ai).concealed.count) tiles")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(Theme.goldDeep)
                if vm.aiThinking {
                    ProgressView().controlSize(.mini)
                }
            }
            OpponentHandView(
                concealedCount: vm.handState.hand(for: .ai).concealed.count,
                bonus: vm.handState.hand(for: .ai).bonus
            )
        }
    }

    // MARK: - Player

    private var playerRow: some View {
        VStack(spacing: 6) {
            HStack(spacing: 8) {
                Text("Your hand")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(Theme.goldDeep)
                if !vm.handState.hand(for: .player).bonus.isEmpty {
                    Text("·")
                    Text("Bonus:")
                        .font(.system(size: 11, weight: .regular))
                        .foregroundStyle(Theme.plum.opacity(0.85))
                    HStack(spacing: 2) {
                        ForEach(Array(vm.handState.hand(for: .player).bonus.enumerated()), id: \.offset) { _, t in
                            TileView(tile: t, size: CGSize(width: 22, height: 30))
                        }
                    }
                }
                Spacer()
            }
            .padding(.horizontal, 16)

            HandView(
                tiles: vm.handState.hand(for: .player).concealed,
                selectable: vm.isAwaitingPlayerDiscard,
                onTap: { tile in
                    vm.playerDiscard(tile)
                }
            )
            .padding(.horizontal, 8)
        }
    }

    // MARK: - Action bar

    private var actionBar: some View {
        HStack(spacing: 12) {
            if vm.isAwaitingPlayerDraw {
                actionButton("Draw") { vm.playerDraw() }
            }
            if vm.canDeclareWin {
                actionButton("🎉 Declare Win", style: .primary) {
                    vm.playerDeclareWin()
                }
            }
            if vm.isAwaitingPlayerClaim {
                if let tile = vm.pendingClaimTile {
                    HStack(spacing: 8) {
                        Text("Claim?")
                            .font(.system(size: 13, weight: .medium))
                        TileView(tile: tile, size: CGSize(width: 32, height: 44))
                    }
                    actionButton("Pass") { vm.playerPassClaim() }
                }
            }
            if vm.isAwaitingPlayerDiscard {
                Text("Tap a tile to discard")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(Theme.goldDeep.opacity(0.7))
            }
            Spacer()
        }
    }

    @ViewBuilder
    private func actionButton(_ label: String, style: ButtonStyleKind = .normal, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(label)
                .font(.system(size: 14, weight: .semibold, design: .rounded))
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(
                    RoundedRectangle(cornerRadius: 10)
                        .fill(style == .primary ? Theme.win : Theme.gold)
                )
                .foregroundStyle(.white)
        }
        .buttonStyle(.plain)
    }

    private enum ButtonStyleKind { case normal, primary }

    // MARK: - Error banner

    @ViewBuilder
    private var errorBanner: some View {
        if let err = vm.lastError {
            Text(err)
                .font(.system(size: 12, weight: .medium))
                .padding(8)
                .background(
                    RoundedRectangle(cornerRadius: 8).fill(Theme.loss.opacity(0.92))
                )
                .foregroundStyle(.white)
                .padding(.top, 8)
                .transition(.opacity)
        }
    }

    // MARK: - End-of-hand overlay

    @ViewBuilder
    private var handEndedOverlay: some View {
        if vm.awaitingNextHand {
            ZStack {
                Color.black.opacity(0.45).ignoresSafeArea()
                HandOutcomeCard(state: vm.handState, recentUnlocks: vm.recentUnlocks) {
                    vm.continueAfterHand()
                }
            }
            .transition(.opacity)
        }
    }

    @ViewBuilder
    private var shopOverlay: some View {
        if vm.awaitingShop, let shop = vm.shop {
            ZStack {
                Color.black.opacity(0.55).ignoresSafeArea()
                if let pack = vm.openedPack {
                    PackPickerView(
                        pack: pack,
                        alreadyPicked: vm.openedPackChoices,
                        onPickCharm: { c in vm.pickFromPack(.charm(c)) },
                        onPickConstellation: { c in vm.pickFromPack(.constellation(c)) },
                        onPickSpell: { s in vm.pickFromPack(.spell(s)) },
                        onSkip: { vm.skipPack() }
                    )
                } else {
                    ShopView(
                        shop: shop,
                        coins: vm.run.coins,
                        canAddCharm: vm.run.canAddCharm,
                        onBuyCharm: { offer in vm.buyCharm(offer) },
                        onBuyPack: { vm.buyPack() },
                        onReroll: { vm.reroll() },
                        onSkip: { vm.closeShop() }
                    )
                }
            }
            .transition(.opacity)
        }
    }

    @ViewBuilder
    private var runCompleteOverlay: some View {
        if vm.runEnded && !vm.awaitingNextHand {
            ZStack {
                Color.black.opacity(0.65).ignoresSafeArea()
                RunCompleteView(run: vm.run, onStartNew: {
                    vm.startNewRun()
                })
            }
            .transition(.opacity)
        }
    }
}

/// Per-hand outcome card shown over GameView when a hand ends.
struct HandOutcomeCard: View {
    let state: HandState
    let recentUnlocks: [String]
    let onContinue: () -> Void

    var body: some View {
        VStack(spacing: 14) {
            outcomeHeader
            if case .win(_, let score, _) = state.outcome {
                VStack(spacing: 4) {
                    ForEach(Array(score.reasons.enumerated()), id: \.offset) { _, reason in
                        HStack {
                            Text(reason.label).font(.system(size: 14, weight: .medium))
                            Spacer()
                            Text("+\(reason.faan)")
                                .font(.system(size: 14, weight: .semibold, design: .serif))
                                .foregroundStyle(Theme.goldDeep)
                        }
                    }
                    Divider()
                    HStack {
                        Text("Total faan").font(.system(size: 14, weight: .semibold))
                        Spacer()
                        Text("\(score.faan)")
                            .font(.system(size: 16, weight: .bold, design: .serif))
                            .foregroundStyle(Theme.goldDeep)
                    }
                }
                .padding(.horizontal, 18)
            }

            if !recentUnlocks.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text("New unlocks")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundStyle(Theme.plum)
                    ForEach(recentUnlocks, id: \.self) { name in
                        Text("🌟 \(name)")
                            .font(.system(size: 12, weight: .medium))
                    }
                }
                .padding(.horizontal, 18)
            }

            Button(action: onContinue) {
                Text("Continue")
                    .font(.system(size: 16, weight: .semibold, design: .rounded))
                    .padding(.horizontal, 28)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 12).fill(Theme.gold)
                    )
                    .foregroundStyle(.white)
            }
            .buttonStyle(.plain)
        }
        .padding(.vertical, 22)
        .padding(.horizontal, 12)
        .frame(maxWidth: 360)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Theme.lanai)
                .shadow(color: .black.opacity(0.3), radius: 16, y: 8)
        )
        .padding(40)
    }

    @ViewBuilder
    private var outcomeHeader: some View {
        switch state.outcome {
        case .win(let seat, _, _):
            if seat == .player {
                Text("You win the hand")
                    .font(.custom(Theme.displayFont, size: 22))
                    .foregroundStyle(Theme.win)
            } else {
                Text("AI takes this hand")
                    .font(.custom(Theme.displayFont, size: 22))
                    .foregroundStyle(Theme.loss)
            }
        case .wallExhausted:
            Text("Wall exhausted — draw game")
                .font(.custom(Theme.displayFont, size: 20))
                .foregroundStyle(Theme.windInk)
        case .none:
            EmptyView()
        }
    }
}
