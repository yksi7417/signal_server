import SwiftUI
import Engine

/// First-launch welcome card. Explains the starter kit (Crystal Lens charm
/// + 2× The Swap spell) and the basic loop. Shown over the home screen the
/// first time the app opens; dismiss is tracked via @AppStorage.
struct TutorialIntroCard: View {
    var onDismiss: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            VStack(spacing: 4) {
                Text("Welcome")
                    .font(.custom(Theme.displayFont, size: 28))
                    .foregroundStyle(Theme.windInk)
                Text("Mahjong+× tutorial — Tables 1 & 2")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(Theme.shadow)
            }

            VStack(alignment: .leading, spacing: 12) {
                bullet("👁",
                    title: "Crystal Lens",
                    body: "A starter Charm. See the AI's tiles all run.")
                bullet("✨",
                    title: "The Swap × 2",
                    body: "Starter Spells. Tap one in the inventory rail, pick a tile to give up, then pick any undrawn wall tile to take.")
                bullet("🪙",
                    title: "Win → spend",
                    body: "Faan becomes coins. Between hands, the shop opens — buy charms or boosters.")
                bullet("👑",
                    title: "Boss hands",
                    body: "Hand 4 of each Table is Boss — random modifier (Whiteout, Frozen Suit, Long Night).")
            }
            .padding(.horizontal, 6)

            Button(action: onDismiss) {
                Text("Got it — let's play")
                    .font(.system(size: 16, weight: .semibold, design: .rounded))
                    .padding(.horizontal, 24)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 12).fill(Theme.gold)
                    )
                    .foregroundStyle(.white)
            }
            .buttonStyle(.plain)
        }
        .padding(22)
        .background(
            RoundedRectangle(cornerRadius: 18)
                .fill(Theme.lanai)
                .shadow(color: .black.opacity(0.3), radius: 16, y: 8)
        )
        .frame(maxWidth: 360)
        .padding(20)
    }

    private func bullet(_ icon: String, title: String, body: String) -> some View {
        HStack(alignment: .top, spacing: 10) {
            Text(icon).font(.system(size: 22))
                .frame(width: 26)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.system(size: 14, weight: .semibold, design: .rounded))
                    .foregroundStyle(Theme.windInk)
                Text(body)
                    .font(.system(size: 12, weight: .regular))
                    .foregroundStyle(Theme.windInk.opacity(0.75))
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 0)
        }
    }
}
