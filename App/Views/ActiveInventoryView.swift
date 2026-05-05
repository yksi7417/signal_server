import SwiftUI
import Engine

/// A horizontally-scrolling rail of the active charms + consumables. Sits in
/// the game header so the player can see what's affecting their score.
struct ActiveInventoryView: View {
    let charms: [Charm]
    let consumables: [Consumable]
    var onUseConsumable: ((String) -> Void)? = nil

    var body: some View {
        if charms.isEmpty && consumables.isEmpty {
            HStack {
                Text("No charms yet — buy some at the shop")
                    .font(.system(size: 11, weight: .regular))
                    .foregroundStyle(Theme.shadow)
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 4)
        } else {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 6) {
                    ForEach(charms, id: \.id) { charm in
                        miniCharm(charm)
                    }
                    ForEach(consumables, id: \.id) { c in
                        miniConsumable(c)
                    }
                }
                .padding(.horizontal, 16)
            }
            .padding(.bottom, 4)
        }
    }

    private func miniCharm(_ charm: Charm) -> some View {
        HStack(spacing: 4) {
            Circle()
                .fill(rarityColor(charm.rarity))
                .frame(width: 6, height: 6)
            Text(charm.name)
                .font(.system(size: 11, weight: .medium))
                .foregroundStyle(Theme.windInk)
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(
            Capsule().fill(Theme.tileFace)
                .overlay(Capsule().stroke(Theme.gold.opacity(0.45), lineWidth: 1))
        )
    }

    private func miniConsumable(_ c: Consumable) -> some View {
        let icon: String = {
            if case .constellation = c { "🌙" } else { "✨" }
        }()
        return Button {
            onUseConsumable?(c.id)
        } label: {
            HStack(spacing: 4) {
                Text(icon).font(.system(size: 10))
                Text(c.name)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundStyle(Theme.windInk)
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(
                Capsule().fill(Theme.tileFace)
                    .overlay(Capsule().stroke(Theme.plum.opacity(0.45), lineWidth: 1))
            )
        }
        .buttonStyle(.plain)
    }

    private func rarityColor(_ rarity: Charm.Rarity) -> Color {
        switch rarity {
        case .common:    return Theme.shadow
        case .uncommon:  return Theme.jade
        case .rare:      return Theme.plum
        case .legendary: return Theme.gold
        }
    }
}
