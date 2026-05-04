/// A Constellation is a consumable that levels up a target pattern's
/// (base, mult) for the rest of the run. Up to 2 in the consumable slot
/// (shared with Spells).
public struct Constellation: Codable, Sendable, Hashable, Identifiable {
    public let id: String
    public let name: String
    public let target: Target
    public let baseDelta: Int
    public let multDelta: Double
    public let rarity: Rarity
    public let description: String

    public init(
        id: String,
        name: String,
        target: Target,
        baseDelta: Int,
        multDelta: Double,
        rarity: Rarity = .common,
        description: String? = nil
    ) {
        self.id = id
        self.name = name
        self.target = target
        self.baseDelta = baseDelta
        self.multDelta = multDelta
        self.rarity = rarity
        self.description = description ?? Self.defaultDescription(
            target: target, baseDelta: baseDelta, multDelta: multDelta
        )
    }

    public enum Target: Codable, Sendable, Hashable {
        case pattern(Pattern)
        case allPatterns
        case bonusTiles
    }

    public enum Rarity: String, Codable, Sendable, Hashable {
        case common, uncommon, rare
    }

    private static func defaultDescription(target: Target, baseDelta: Int, multDelta: Double) -> String {
        let what: String
        switch target {
        case .pattern(let p): what = p.chinese
        case .allPatterns:    what = "All patterns"
        case .bonusTiles:     what = "Flowers & Seasons bonuses"
        }
        return "\(what): +\(baseDelta) base, +\(multDelta.formatted) mult"
    }
}

private extension Double {
    /// One-decimal formatting without depending on Foundation.
    var formatted: String {
        let rounded = (self * 10).rounded()
        let whole = Int(rounded / 10)
        let dec = Int(abs(rounded.truncatingRemainder(dividingBy: 10)))
        return "\(whole).\(dec)"
    }
}

public enum ConstellationCatalog {

    public static let starter: [Constellation] = [
        Constellation(id: "orion", name: "Orion",
                      target: .pattern(.duiDui),
                      baseDelta: 10, multDelta: 0.5),
        Constellation(id: "cassiopeia", name: "Cassiopeia",
                      target: .pattern(.ping),
                      baseDelta: 10, multDelta: 0.5),
        Constellation(id: "lyra", name: "Lyra",
                      target: .pattern(.hunYiSe),
                      baseDelta: 15, multDelta: 0.5),
        Constellation(id: "phoenix", name: "Phoenix",
                      target: .pattern(.qingYiSe),
                      baseDelta: 20, multDelta: 1.0,
                      rarity: .uncommon),
        Constellation(id: "big_dipper", name: "Big Dipper",
                      target: .pattern(.duiDui),
                      baseDelta: 5, multDelta: 1.0,
                      rarity: .uncommon),
        Constellation(id: "pleiades", name: "Pleiades",
                      target: .allPatterns,
                      baseDelta: 5, multDelta: 0.2,
                      rarity: .uncommon),
        Constellation(id: "andromeda", name: "Andromeda",
                      target: .bonusTiles,
                      baseDelta: 10, multDelta: 0,
                      rarity: .uncommon),
        Constellation(id: "draco", name: "Draco",
                      target: .pattern(.qingYiSe),
                      baseDelta: 30, multDelta: 1.5,
                      rarity: .rare),
    ]

    public static func constellation(id: String) -> Constellation? {
        starter.first(where: { $0.id == id })
    }
}
