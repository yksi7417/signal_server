import SwiftUI
import Engine

/// End-of-run screen. Shows totals + offers to start a new run.
struct RunCompleteView: View {
    let run: Run
    var onStartNew: () -> Void

    var body: some View {
        VStack(spacing: 18) {
            VStack(spacing: 4) {
                Text(headerTitle)
                    .font(.custom(Theme.displayFont, size: 28))
                    .foregroundStyle(headerColor)
                Text(headerSubtitle)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(Theme.shadow)
            }

            statsGrid

            VStack(alignment: .leading, spacing: 6) {
                Text("Wins by pattern")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(Theme.goldDeep)
                ForEach(Pattern.allCases, id: \.self) { p in
                    let n = run.stats.winsByPattern[p, default: 0]
                    if n > 0 {
                        HStack {
                            Text("\(p.chinese) \(p.english)")
                                .font(.system(size: 12, weight: .medium))
                            Spacer()
                            Text("×\(n)")
                                .font(.system(size: 12, weight: .semibold, design: .serif))
                                .foregroundStyle(Theme.goldDeep)
                        }
                    }
                }
            }

            Button(action: onStartNew) {
                Text("Start a New Run")
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
        .padding(22)
        .background(
            RoundedRectangle(cornerRadius: 18)
                .fill(Theme.lanai)
                .shadow(color: .black.opacity(0.3), radius: 16, y: 8)
        )
        .frame(maxWidth: 360)
        .padding(20)
    }

    private var headerTitle: String {
        run.status == .completed ? "Run complete" : "Run ended"
    }

    private var headerSubtitle: String {
        switch run.status {
        case .completed: return "Beat all MVP Tables"
        case .failed:    return "Try a new seed"
        case .inProgress: return ""
        }
    }

    private var headerColor: Color {
        run.status == .completed ? Theme.win : Theme.coral
    }

    private var statsGrid: some View {
        let cols = [GridItem(.flexible()), GridItem(.flexible())]
        return LazyVGrid(columns: cols, spacing: 8) {
            stat("Hands won", "\(run.stats.handsWon)")
            stat("Hands lost", "\(run.stats.handsLost)")
            stat("Total faan", "\(run.stats.totalFaan)")
            stat("Coins earned", "\(run.stats.totalCoinsEarned)")
            stat("Sweeps", "\(run.stats.tableSweepCount)")
            stat("Spells used", "\(run.stats.spellsUsed)")
        }
    }

    private func stat(_ label: String, _ value: String) -> some View {
        VStack(spacing: 2) {
            Text(value)
                .font(.system(size: 22, weight: .bold, design: .serif))
                .foregroundStyle(Theme.windInk)
            Text(label)
                .font(.system(size: 10, weight: .medium))
                .foregroundStyle(Theme.shadow)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(Theme.tileFace)
        )
    }
}
