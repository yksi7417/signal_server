import SwiftUI
import Engine

/// Between-hand shop. Two charms for sale, one booster pack, reroll, skip.
struct ShopView: View {
    let shop: Shop
    let coins: Int
    let canAddCharm: Bool

    var onBuyCharm: (ShopCharm) -> Void
    var onBuyPack: () -> Void
    var onReroll: () -> Void
    var onSkip: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            header

            if shop.charms.isEmpty {
                Text("Charms sold out")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(Theme.shadow)
                    .padding(.vertical, 6)
            } else {
                VStack(spacing: 8) {
                    ForEach(shop.charms) { offer in
                        CharmChip(
                            charm: offer.charm,
                            price: offer.price,
                            onTap: {
                                guard coins >= offer.price, canAddCharm else { return }
                                onBuyCharm(offer)
                            }
                        )
                        .opacity(coins >= offer.price && canAddCharm ? 1.0 : 0.55)
                    }
                }
            }

            packCard

            HStack(spacing: 12) {
                rerollButton
                Spacer()
                skipButton
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 18)
                .fill(Theme.lanai)
                .shadow(color: .black.opacity(0.25), radius: 16, y: 8)
        )
        .frame(maxWidth: 380)
        .padding(20)
    }

    // MARK: - Subviews

    private var header: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("Shop")
                    .font(.custom(Theme.displayFont, size: 26))
                    .foregroundStyle(Theme.windInk)
                Text("Spend coins between hands")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundStyle(Theme.shadow)
            }
            Spacer()
            HStack(spacing: 6) {
                Circle().fill(Theme.gold).frame(width: 12, height: 12)
                Text("\(coins)")
                    .font(.system(size: 22, weight: .semibold, design: .serif))
                    .foregroundStyle(Theme.goldDeep)
            }
        }
    }

    private var packCard: some View {
        Button(action: {
            guard coins >= shop.pack.price else { return }
            onBuyPack()
        }) {
            HStack(spacing: 12) {
                ZStack {
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Theme.coral.opacity(0.3))
                        .frame(width: 50, height: 60)
                    Text("📦")
                        .font(.system(size: 28))
                }
                VStack(alignment: .leading, spacing: 3) {
                    Text(shop.pack.displayName)
                        .font(.system(size: 14, weight: .semibold, design: .rounded))
                        .foregroundStyle(Theme.windInk)
                    Text(packDescription)
                        .font(.system(size: 11, weight: .regular))
                        .foregroundStyle(Theme.windInk.opacity(0.7))
                        .multilineTextAlignment(.leading)
                }
                Spacer()
                priceTag(shop.pack.price)
            }
            .padding(10)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Theme.tileFace)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Theme.coral.opacity(0.5), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(.plain)
        .opacity(coins >= shop.pack.price ? 1.0 : 0.55)
    }

    private var packDescription: String {
        switch shop.pack {
        case .charmSmall:    return "3 Charms — pick 1"
        case .charmLarge:    return "5 Charms — pick 2"
        case .constellation: return "3 Constellations — pick 1"
        case .spellSmall:    return "3 Spells — pick 1"
        case .spellMega:     return "5 Spells — pick 2"
        case .mixed:         return "2 of each — pick 1 of each"
        }
    }

    private var rerollButton: some View {
        Button(action: onReroll) {
            HStack(spacing: 4) {
                Image(systemName: "arrow.triangle.2.circlepath")
                    .font(.system(size: 11))
                Text("Reroll")
                    .font(.system(size: 13, weight: .medium, design: .rounded))
                priceTag(shop.rerollCost)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(Theme.wicker.opacity(0.6))
            )
            .foregroundStyle(Theme.windInk)
        }
        .buttonStyle(.plain)
        .disabled(coins < shop.rerollCost)
        .opacity(coins >= shop.rerollCost ? 1.0 : 0.5)
    }

    private var skipButton: some View {
        Button(action: onSkip) {
            Text("Skip → Next Hand")
                .font(.system(size: 14, weight: .semibold, design: .rounded))
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(
                    RoundedRectangle(cornerRadius: 10).fill(Theme.gold)
                )
                .foregroundStyle(.white)
        }
        .buttonStyle(.plain)
    }
}
