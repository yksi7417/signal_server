/// The 15 starter Charms from the design doc.
///
/// IDs are stable; pricing/rarity used by Shop. Order matches the design-doc
/// table for traceability.
public enum CharmCatalog {

    public static let starter: [Charm] = [
        // 1. East Wind Whisper
        Charm(
            id: "east_wind_whisper", name: "East Wind Whisper",
            rarity: .common,
            description: "+10 base score on East hands.",
            effect: .windHandBase(wind: .east, amount: 10)
        ),
        // 2. South Wind Sails
        Charm(
            id: "south_wind_sails", name: "South Wind Sails",
            rarity: .common,
            description: "+10 base score on South hands.",
            effect: .windHandBase(wind: .south, amount: 10)
        ),
        // 3. West Wind Patience
        Charm(
            id: "west_wind_patience", name: "West Wind Patience",
            rarity: .common,
            description: "+10 base score on West hands.",
            effect: .windHandBase(wind: .west, amount: 10)
        ),
        // 4. North Star
        Charm(
            id: "north_star", name: "North Star",
            rarity: .common,
            description: "+10 base score on North (Boss) hands.",
            effect: .windHandBase(wind: .north, amount: 10)
        ),
        // 5. Cookie Jar
        Charm(
            id: "cookie_jar", name: "Cookie Jar",
            rarity: .common,
            description: "Cookies in winning hand: ×3 mult.",
            effect: .suitMult(suit: .cookies, factor: 3.0)
        ),
        // 6. Bamboo Forest
        Charm(
            id: "bamboo_forest", name: "Bamboo Forest",
            rarity: .common,
            description: "Each Bamboo tile in winning hand: +5 base.",
            effect: .perTileSuitBase(suit: .bamboo, amount: 5)
        ),
        // 7. Scholar's Quill
        Charm(
            id: "scholars_quill", name: "Scholar's Quill",
            rarity: .common,
            description: "Characters in winning hand: ×2 mult.",
            effect: .suitMult(suit: .characters, factor: 2.0)
        ),
        // 8. Dragon's Breath
        Charm(
            id: "dragons_breath", name: "Dragon's Breath",
            rarity: .uncommon,
            description: "Each Dragon in hand: +20 base.",
            effect: .perDragonBase(amount: 20)
        ),
        // 9. Pair Charm
        Charm(
            id: "pair_charm", name: "Pair Charm",
            rarity: .common,
            description: "Each pair scored: +15 base.",
            effect: .perPairBase(amount: 15)
        ),
        // 10. Pung Power
        Charm(
            id: "pung_power", name: "Pung Power",
            rarity: .uncommon,
            description: "Each pung scored: ×1.5 mult.",
            effect: .perPungMult(factor: 1.5)
        ),
        // 11. Sequence Sage
        Charm(
            id: "sequence_sage", name: "Sequence Sage",
            rarity: .common,
            description: "Each chow scored: +10 base.",
            effect: .perChowBase(amount: 10)
        ),
        // 12. Lucky Spell
        Charm(
            id: "lucky_spell", name: "Lucky Spell",
            rarity: .rare,
            description: "Each Spell used adds +0.1 mult permanently.",
            effect: .spellMultGrowth(per: 0.1)
        ),
        // 13. The Hostess
        Charm(
            id: "the_hostess", name: "The Hostess",
            rarity: .common,
            description: "+5 coins per hand won.",
            effect: .coinsPerWin(amount: 5)
        ),
        // 14. Charleston Queen (T5+; inert in MVP)
        Charm(
            id: "charleston_queen", name: "Charleston Queen",
            rarity: .rare,
            description: "Skip Charleston for +50 base. (T5+)",
            effect: .skipCharlestonBonus(amount: 50)
        ),
        // 15. Four Winds Aligned
        Charm(
            id: "four_winds_aligned", name: "Four Winds Aligned",
            rarity: .legendary,
            description: "Sweep a Table: ×3 mult on next Table's first hand.",
            effect: .nextTableSweepMult(factor: 3.0)
        ),
        // 16. Crystal Lens — tutorial / x-ray utility charm.
        Charm(
            id: "crystal_lens", name: "Crystal Lens",
            rarity: .legendary,
            description: "See your opponent's concealed tiles.",
            effect: .revealOpponentHand
        ),
    ]

    /// Lookup by id.
    public static func charm(id: String) -> Charm? {
        starter.first(where: { $0.id == id })
    }

    public static func charms(by rarity: Charm.Rarity) -> [Charm] {
        starter.filter { $0.rarity == rarity }
    }
}
