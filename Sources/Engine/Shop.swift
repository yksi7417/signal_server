/// Booster pack types from the design doc.
public enum BoosterPack: Codable, Sendable, Hashable {
    case charmSmall    // 3 Charms, pick 1, $4
    case charmLarge    // 5 Charms, pick 2, $7
    case constellation // 3 Constellations, pick 1, $4
    case spellSmall    // 3 Spells, pick 1, $3
    case spellMega     // 5 Spells, pick 2, $6
    case mixed         // 2 of each, pick 1 of each, $10 (rare)

    public var price: Int {
        switch self {
        case .charmSmall:    return 4
        case .charmLarge:    return 7
        case .constellation: return 4
        case .spellSmall:    return 3
        case .spellMega:     return 6
        case .mixed:         return 10
        }
    }

    public var displayName: String {
        switch self {
        case .charmSmall:    return "Charm Pack (small)"
        case .charmLarge:    return "Charm Pack (large)"
        case .constellation: return "Constellation Pack"
        case .spellSmall:    return "Spell Pack"
        case .spellMega:     return "Spell Pack (mega)"
        case .mixed:         return "Mixed Pack"
        }
    }
}

/// One offered charm in the shop, with its purchase price.
public struct ShopCharm: Codable, Sendable, Hashable, Identifiable {
    public let charm: Charm
    public let price: Int

    public init(charm: Charm, price: Int) {
        self.charm = charm
        self.price = price
    }

    public var id: String { charm.id }
}

/// An open shop offer. Re-rolled (new instance) on reroll.
public struct Shop: Codable, Sendable, Hashable {
    public var charms: [ShopCharm]
    public var pack: BoosterPack
    public var rerollCost: Int
    public var rerollsUsed: Int

    public init(
        charms: [ShopCharm],
        pack: BoosterPack,
        rerollCost: Int = 1,
        rerollsUsed: Int = 0
    ) {
        self.charms = charms
        self.pack = pack
        self.rerollCost = rerollCost
        self.rerollsUsed = rerollsUsed
    }
}

/// Pricing for individual charms at sale.
public enum CharmPricing {
    public static func price(for charm: Charm) -> Int {
        switch charm.rarity {
        case .common:    return 4
        case .uncommon:  return 6
        case .rare:      return 8
        case .legendary: return 12
        }
    }
}

public enum ShopRoller {

    /// The default odds curve for booster pack selection. Mixed pack is rare.
    public static let defaultPackWeights: [(BoosterPack, Int)] = [
        (.charmSmall, 30),
        (.charmLarge, 15),
        (.constellation, 20),
        (.spellSmall, 20),
        (.spellMega, 10),
        (.mixed, 5),
    ]

    /// Roll a fresh shop offer. Always 2 charms + 1 booster pack.
    public static func rollShop<G: RandomNumberGenerator>(
        unlocked: UnlockedPool,
        currentTable: Int,
        rng: inout G,
        rerollsUsed: Int = 0
    ) -> Shop {
        let charms = pickN(2, from: unlocked.charms, rng: &rng).map {
            ShopCharm(charm: $0, price: CharmPricing.price(for: $0))
        }
        let pack = weightedPick(defaultPackWeights, rng: &rng)
        return Shop(
            charms: charms,
            pack: pack,
            rerollCost: 1 + rerollsUsed,   // escalating reroll cost
            rerollsUsed: rerollsUsed
        )
    }

    /// Open a booster pack — produce the offered set from the unlocked pool.
    /// The caller picks the allowed number of items via Run.add* APIs.
    public static func openPack<G: RandomNumberGenerator>(
        _ pack: BoosterPack,
        unlocked: UnlockedPool,
        currentTable: Int,
        rng: inout G
    ) -> PackContents {
        switch pack {
        case .charmSmall:
            return .init(charms: pickN(3, from: unlocked.charms, rng: &rng), pickCount: 1)
        case .charmLarge:
            return .init(charms: pickN(5, from: unlocked.charms, rng: &rng), pickCount: 2)
        case .constellation:
            return .init(constellations: pickN(3, from: unlocked.constellations, rng: &rng), pickCount: 1)
        case .spellSmall:
            let pool = unlocked.spells.filter { $0.minTable <= currentTable }
            return .init(spells: pickN(3, from: pool, rng: &rng), pickCount: 1)
        case .spellMega:
            let pool = unlocked.spells.filter { $0.minTable <= currentTable }
            return .init(spells: pickN(5, from: pool, rng: &rng), pickCount: 2)
        case .mixed:
            let pool = unlocked.spells.filter { $0.minTable <= currentTable }
            return .init(
                charms: pickN(2, from: unlocked.charms, rng: &rng),
                constellations: pickN(2, from: unlocked.constellations, rng: &rng),
                spells: pickN(2, from: pool, rng: &rng),
                pickCount: 3   // 1 of each
            )
        }
    }

    // MARK: - Helpers

    private static func pickN<T, G: RandomNumberGenerator>(_ n: Int, from pool: [T], rng: inout G) -> [T] {
        guard !pool.isEmpty else { return [] }
        var copy = pool
        copy.shuffle(using: &rng)
        return Array(copy.prefix(n))
    }

    private static func weightedPick<T, G: RandomNumberGenerator>(_ weighted: [(T, Int)], rng: inout G) -> T {
        let total = weighted.reduce(0) { $0 + $1.1 }
        var roll = Int.random(in: 0..<total, using: &rng)
        for (item, weight) in weighted {
            if roll < weight { return item }
            roll -= weight
        }
        return weighted.last!.0
    }
}

/// Contents of an opened booster pack.
public struct PackContents: Codable, Sendable, Hashable {
    public var charms: [Charm]
    public var constellations: [Constellation]
    public var spells: [Spell]
    public var pickCount: Int

    public init(
        charms: [Charm] = [],
        constellations: [Constellation] = [],
        spells: [Spell] = [],
        pickCount: Int
    ) {
        self.charms = charms
        self.constellations = constellations
        self.spells = spells
        self.pickCount = pickCount
    }
}

/// What's currently unlocked and available to roll. Phase 11's UnlockStore
/// produces this. For testing/CLI we can pass `.all`.
public struct UnlockedPool: Codable, Sendable, Hashable {
    public var charms: [Charm]
    public var constellations: [Constellation]
    public var spells: [Spell]

    public init(charms: [Charm], constellations: [Constellation], spells: [Spell]) {
        self.charms = charms
        self.constellations = constellations
        self.spells = spells
    }

    /// Everything unlocked — used by tests and the CLI driver.
    public static let all = UnlockedPool(
        charms: CharmCatalog.starter,
        constellations: ConstellationCatalog.starter,
        spells: SpellCatalog.starter
    )
}
