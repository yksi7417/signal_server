import SwiftUI
import Engine

/// Header strip: prevailing wind, table/hand, coin balance, score readout.
struct RunStatusView: View {
    let table: Int
    let handIndex: Int
    let prevailingWind: Wind
    let coins: Int
    let bossModifier: BossModifier?

    var body: some View {
        VStack(spacing: 6) {
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Table \(table) · Hand \(handIndex)")
                        .font(.system(size: 13, weight: .medium, design: .rounded))
                        .foregroundStyle(Theme.goldDeep)
                    Text(prevailingWind.label)
                        .font(.custom(Theme.displayFont, size: 22))
                        .foregroundStyle(Theme.windInk)
                }
                Spacer()
                HStack(spacing: 6) {
                    Image(systemName: "circle.hexagonpath.fill")
                        .font(.system(size: 14))
                        .foregroundStyle(Theme.gold)
                    Text("\(coins)")
                        .font(.system(size: 22, weight: .semibold, design: .serif))
                        .foregroundStyle(Theme.goldDeep)
                }
            }
            if let mod = bossModifier {
                HStack(spacing: 6) {
                    Text("👑")
                    Text("\(mod.displayName) — \(mod.description)")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundStyle(Theme.coral)
                }
                .padding(.vertical, 4)
                .padding(.horizontal, 10)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Theme.coral.opacity(0.13))
                )
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
    }
}
