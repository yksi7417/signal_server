import SwiftUI
import Engine

/// Compact representation of a Charm — used in shop offers, pack pickers,
/// and the active-inventory bar in the game header.
struct CharmChip: View {
    let charm: Charm
    var price: Int? = nil
    var onTap: (() -> Void)? = nil

    var body: some View {
        Button(action: { onTap?() }) {
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 6) {
                    rarityDot
                    Text(charm.name)
                        .font(.system(size: 13, weight: .semibold, design: .rounded))
                        .foregroundStyle(Theme.windInk)
                        .lineLimit(1)
                    Spacer(minLength: 4)
                    if let price {
                        priceTag(price)
                    }
                }
                Text(charm.description)
                    .font(.system(size: 11, weight: .regular))
                    .foregroundStyle(Theme.windInk.opacity(0.7))
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)
            }
            .padding(10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Theme.tileFace)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Theme.gold.opacity(0.45), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(.plain)
        .disabled(onTap == nil)
    }

    private var rarityDot: some View {
        Circle()
            .fill(rarityColor)
            .frame(width: 8, height: 8)
    }

    private var rarityColor: Color {
        switch charm.rarity {
        case .common:    return Theme.shadow
        case .uncommon:  return Theme.jade
        case .rare:      return Theme.plum
        case .legendary: return Theme.gold
        }
    }
}

/// Compact representation of a Constellation.
struct ConstellationChip: View {
    let constellation: Constellation
    var onTap: (() -> Void)? = nil

    var body: some View {
        Button(action: { onTap?() }) {
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 6) {
                    Text("🌙").font(.system(size: 12))
                    Text(constellation.name)
                        .font(.system(size: 13, weight: .semibold, design: .rounded))
                        .foregroundStyle(Theme.windInk)
                        .lineLimit(1)
                    Spacer()
                }
                Text(constellation.description)
                    .font(.system(size: 11))
                    .foregroundStyle(Theme.windInk.opacity(0.7))
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)
            }
            .padding(10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Theme.tileFace)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Theme.plum.opacity(0.45), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(.plain)
        .disabled(onTap == nil)
    }
}

/// Compact representation of a Spell.
struct SpellChip: View {
    let spell: Spell
    var onTap: (() -> Void)? = nil

    var body: some View {
        Button(action: { onTap?() }) {
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 6) {
                    Text("✨").font(.system(size: 12))
                    Text(spell.name)
                        .font(.system(size: 13, weight: .semibold, design: .rounded))
                        .foregroundStyle(Theme.windInk)
                        .lineLimit(1)
                    Spacer()
                    if spell.minTable > 1 {
                        Text("T\(spell.minTable)+")
                            .font(.system(size: 10, weight: .medium))
                            .padding(.horizontal, 5)
                            .padding(.vertical, 1)
                            .background(
                                Capsule().fill(Theme.coral.opacity(0.18))
                            )
                            .foregroundStyle(Theme.coral)
                    }
                }
                Text(spell.description)
                    .font(.system(size: 11))
                    .foregroundStyle(Theme.windInk.opacity(0.7))
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)
            }
            .padding(10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Theme.tileFace)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Theme.coral.opacity(0.45), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(.plain)
        .disabled(onTap == nil)
    }
}

/// Tiny price chip (gold coin + number).
@ViewBuilder
func priceTag(_ price: Int) -> some View {
    HStack(spacing: 3) {
        Circle()
            .fill(Theme.gold)
            .frame(width: 10, height: 10)
        Text("\(price)")
            .font(.system(size: 13, weight: .semibold, design: .serif))
            .foregroundStyle(Theme.goldDeep)
    }
    .padding(.horizontal, 6)
    .padding(.vertical, 2)
    .background(
        Capsule().fill(Theme.gold.opacity(0.12))
    )
}
