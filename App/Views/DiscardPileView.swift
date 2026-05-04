import SwiftUI
import Engine

/// Stylized discard pool — recent discards are always visible, older ones
/// stack behind them. For MVP we show the last N tiles in a flowing grid.
struct DiscardPileView: View {
    let entries: [HandState.DiscardEntry]
    var maxVisible: Int = 24

    var body: some View {
        let recent = Array(entries.suffix(maxVisible))
        VStack(alignment: .leading, spacing: 4) {
            Text("Discards")
                .font(.system(size: 12, weight: .medium, design: .rounded))
                .foregroundStyle(Theme.goldDeep.opacity(0.8))
            LazyVGrid(
                columns: Array(repeating: GridItem(.fixed(36), spacing: 3), count: 8),
                spacing: 4
            ) {
                ForEach(Array(recent.enumerated()), id: \.offset) { _, entry in
                    TileView(
                        tile: entry.tile,
                        size: CGSize(width: 34, height: 46),
                        dimmed: entry.seat == .ai
                    )
                }
            }
        }
        .padding(8)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Theme.wicker.opacity(0.45))
        )
    }
}
