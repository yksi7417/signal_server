import SwiftUI
import Engine

/// Modal sheet shown when a booster pack is opened. The player picks
/// `pack.pickCount` items (across charms/constellations/spells).
struct PackPickerView: View {
    let pack: PackContents
    let alreadyPicked: Int
    var onPickCharm: (Charm) -> Void
    var onPickConstellation: (Constellation) -> Void
    var onPickSpell: (Spell) -> Void
    var onSkip: () -> Void

    var body: some View {
        VStack(spacing: 14) {
            header
            ScrollView {
                VStack(spacing: 8) {
                    ForEach(pack.charms, id: \.id) { c in
                        CharmChip(charm: c, onTap: { onPickCharm(c) })
                    }
                    ForEach(pack.constellations, id: \.id) { c in
                        ConstellationChip(constellation: c, onTap: { onPickConstellation(c) })
                    }
                    ForEach(pack.spells, id: \.id) { s in
                        SpellChip(spell: s, onTap: { onPickSpell(s) })
                    }
                }
            }
            .frame(maxHeight: 380)

            Button(action: onSkip) {
                Text("Done")
                    .font(.system(size: 14, weight: .semibold, design: .rounded))
                    .padding(.horizontal, 24)
                    .padding(.vertical, 8)
                    .background(
                        RoundedRectangle(cornerRadius: 10).fill(Theme.gold)
                    )
                    .foregroundStyle(.white)
            }
            .buttonStyle(.plain)
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 18)
                .fill(Theme.lanai)
                .shadow(color: .black.opacity(0.3), radius: 16, y: 8)
        )
        .frame(maxWidth: 380)
        .padding(20)
    }

    private var header: some View {
        VStack(spacing: 4) {
            Text("Open the pack")
                .font(.custom(Theme.displayFont, size: 22))
                .foregroundStyle(Theme.windInk)
            Text("Pick \(remaining) more")
                .font(.system(size: 12, weight: .medium))
                .foregroundStyle(Theme.coral)
        }
    }

    private var remaining: Int {
        max(0, pack.pickCount - alreadyPicked)
    }
}
