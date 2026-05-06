import SwiftUI
import Engine

/// The player's concealed hand. Tiles are tappable when `onTap` is set; used
/// for selecting which tile to discard.
struct HandView: View {
    let tiles: [Tile]
    var selectable: Bool = false
    var selectedTile: Tile? = nil
    var onTap: ((Tile) -> Void)? = nil

    var body: some View {
        HStack(spacing: 4) {
            ForEach(Array(tiles.enumerated()), id: \.offset) { _, tile in
                Button {
                    onTap?(tile)
                } label: {
                    TileView(
                        tile: tile,
                        dimmed: selectable && selectedTile != nil && selectedTile != tile
                    )
                    .offset(y: selectedTile == tile ? -8 : 0)
                }
                .buttonStyle(.plain)
                .disabled(!selectable)
            }
        }
    }
}

/// AI hand. Face-down by default; if `revealedTiles` is provided (Crystal
/// Lens charm active) the tiles render face up with a soft glow. Bonus
/// tiles always show face up since they're publicly known once set aside.
struct OpponentHandView: View {
    let concealedCount: Int
    let bonus: [Tile]
    var revealedTiles: [Tile]? = nil

    var body: some View {
        VStack(spacing: 4) {
            HStack(spacing: 4) {
                if let revealed = revealedTiles {
                    ForEach(Array(revealed.enumerated()), id: \.offset) { _, tile in
                        TileView(tile: tile, size: CGSize(width: 36, height: 50))
                            .overlay(
                                RoundedRectangle(cornerRadius: 10)
                                    .stroke(Theme.plum.opacity(0.55), lineWidth: 1.5)
                            )
                    }
                } else {
                    ForEach(0..<concealedCount, id: \.self) { _ in
                        TileView(tile: .joker, size: CGSize(width: 36, height: 50), faceUp: false)
                    }
                }
            }
            if !bonus.isEmpty {
                HStack(spacing: 3) {
                    ForEach(Array(bonus.enumerated()), id: \.offset) { _, t in
                        TileView(tile: t, size: CGSize(width: 32, height: 44))
                    }
                }
            }
        }
    }
}
