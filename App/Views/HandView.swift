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

/// AI hand — face-down tiles. Bonus tiles still show face up since they're
/// publicly known once set aside.
struct OpponentHandView: View {
    let concealedCount: Int
    let bonus: [Tile]

    var body: some View {
        VStack(spacing: 4) {
            HStack(spacing: 4) {
                ForEach(0..<concealedCount, id: \.self) { _ in
                    TileView(tile: .joker, size: CGSize(width: 36, height: 50), faceUp: false)
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
