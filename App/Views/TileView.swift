import SwiftUI
import Engine

/// Single tile rendering — placeholder typography until art is commissioned.
/// Suit/rank/honor labels are rendered with the Palm Beach palette.
struct TileView: View {
    let tile: Tile
    var size: CGSize = CGSize(width: 56, height: 76)
    var faceUp: Bool = true
    var dimmed: Bool = false

    var body: some View {
        ZStack {
            tileBody
            if faceUp { face }
        }
        .frame(width: size.width, height: size.height)
        .opacity(dimmed ? 0.45 : 1.0)
    }

    // MARK: - Visual structure

    private var tileBody: some View {
        RoundedRectangle(cornerRadius: 10, style: .continuous)
            .fill(faceUp ? Theme.tileFace : Theme.tileBack)
            .overlay(
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .stroke(Theme.tileEdge, lineWidth: 1)
            )
            .shadow(color: Theme.shadow.opacity(0.45), radius: 2, y: 2)
    }

    @ViewBuilder
    private var face: some View {
        switch tile {
        case .suited(let suit, let rank):
            VStack(spacing: 2) {
                Text("\(rank)")
                    .font(.system(size: size.width * 0.42, weight: .semibold, design: .serif))
                Text(suit.chinese)
                    .font(.system(size: size.width * 0.36, weight: .medium))
            }
            .foregroundStyle(color(for: suit))

        case .wind(let wind):
            Text(wind.chinese)
                .font(.system(size: size.width * 0.66, weight: .bold, design: .serif))
                .foregroundStyle(Theme.windInk)

        case .dragon(let dragon):
            Text(dragon.chinese)
                .font(.system(size: size.width * 0.66, weight: .bold, design: .serif))
                .foregroundStyle(color(for: dragon))

        case .flower(let n):
            VStack(spacing: 1) {
                Text("花").font(.system(size: size.width * 0.32, weight: .medium))
                Text("\(n)").font(.system(size: size.width * 0.4, weight: .semibold, design: .serif))
            }
            .foregroundStyle(Theme.coral)

        case .season(let n):
            VStack(spacing: 1) {
                Text("季").font(.system(size: size.width * 0.32, weight: .medium))
                Text("\(n)").font(.system(size: size.width * 0.4, weight: .semibold, design: .serif))
            }
            .foregroundStyle(Theme.plum)

        case .joker:
            Text("J")
                .font(.system(size: size.width * 0.7, weight: .heavy, design: .serif))
                .foregroundStyle(Theme.gold)
        }
    }

    private func color(for suit: Suit) -> Color {
        switch suit {
        case .cookies:    return Theme.cookies
        case .bamboo:     return Theme.bamboo
        case .characters: return Theme.characters
        }
    }

    private func color(for dragon: Dragon) -> Color {
        switch dragon {
        case .red:   return Theme.dragonRed
        case .green: return Theme.dragonGreen
        case .white: return Theme.dragonWhite
        }
    }
}

#Preview {
    HStack(spacing: 6) {
        TileView(tile: .suited(.cookies, rank: 5))
        TileView(tile: .suited(.bamboo, rank: 9))
        TileView(tile: .suited(.characters, rank: 3))
        TileView(tile: .wind(.east))
        TileView(tile: .dragon(.red))
        TileView(tile: .flower(2))
        TileView(tile: .season(3))
        TileView(tile: .joker)
    }
    .padding()
    .background(Theme.lanai)
}
