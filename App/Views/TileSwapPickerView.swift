import SwiftUI
import Engine

/// Two-step picker for the Tile Swap spell:
/// 1. Player picks a tile from their hand to give up.
/// 2. Player picks an undrawn wall tile to receive.
///
/// Tapping a hand tile in the GameView mid-flow calls `selectHandTile`;
/// tapping a wall tile here calls `commitSwap`.
struct TileSwapPickerView: View {
    let pending: GameViewModel.PendingSwap
    let hand: [Tile]
    let wall: [Tile]
    var onPickHandTile: (Tile) -> Void
    var onPickWallTile: (Int) -> Void
    var onCancel: () -> Void

    var body: some View {
        VStack(spacing: 14) {
            header

            if pending.selectedHandTile == nil {
                handPicker
            } else {
                handPreview
                wallPicker
            }

            Button(action: onCancel) {
                Text("Cancel")
                    .font(.system(size: 13, weight: .medium, design: .rounded))
                    .padding(.horizontal, 16)
                    .padding(.vertical, 6)
                    .background(
                        Capsule().fill(Theme.wicker.opacity(0.8))
                    )
                    .foregroundStyle(Theme.windInk)
            }
            .buttonStyle(.plain)
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 18)
                .fill(Theme.lanai)
                .shadow(color: .black.opacity(0.3), radius: 16, y: 8)
        )
        .frame(maxWidth: 380)
        .padding(20)
    }

    // MARK: - Sections

    private var header: some View {
        VStack(spacing: 4) {
            Text("✨ The Swap")
                .font(.custom(Theme.displayFont, size: 22))
                .foregroundStyle(Theme.windInk)
            Text(promptText)
                .font(.system(size: 12, weight: .medium))
                .foregroundStyle(Theme.coral)
                .multilineTextAlignment(.center)
        }
    }

    private var promptText: String {
        if pending.selectedHandTile == nil {
            return "Step 1 of 2 — pick a tile to give up"
        } else {
            return "Step 2 of 2 — pick an undrawn tile to take"
        }
    }

    private var handPicker: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Your hand")
                .font(.system(size: 11, weight: .semibold))
                .foregroundStyle(Theme.goldDeep)
            HStack(spacing: 5) {
                ForEach(Array(hand.enumerated()), id: \.offset) { _, tile in
                    Button { onPickHandTile(tile) } label: {
                        TileView(tile: tile, size: CGSize(width: 44, height: 60))
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    private var handPreview: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("You're giving up")
                .font(.system(size: 11, weight: .semibold))
                .foregroundStyle(Theme.goldDeep)
            if let t = pending.selectedHandTile {
                TileView(tile: t, size: CGSize(width: 50, height: 68))
            }
        }
    }

    private var wallPicker: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Undrawn wall · \(wall.count) tiles")
                .font(.system(size: 11, weight: .semibold))
                .foregroundStyle(Theme.goldDeep)
            ScrollView(.vertical, showsIndicators: true) {
                LazyVGrid(
                    columns: Array(repeating: GridItem(.fixed(38), spacing: 4), count: 8),
                    spacing: 5
                ) {
                    ForEach(Array(wall.enumerated()), id: \.offset) { idx, tile in
                        Button { onPickWallTile(idx) } label: {
                            TileView(tile: tile, size: CGSize(width: 36, height: 50))
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.bottom, 4)
            }
            .frame(maxHeight: 280)
        }
    }
}
