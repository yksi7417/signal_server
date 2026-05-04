import Testing
@testable import Engine

@Suite("Shop — rolling")
struct ShopRollTests {

    @Test func shopAlwaysHasTwoCharmsAndOnePack() {
        var rng = SeededRandomNumberGenerator(seed: 1)
        let shop = ShopRoller.rollShop(unlocked: .all, currentTable: 1, rng: &rng)
        #expect(shop.charms.count == 2)
        // One pack ≠ a list, so just verify the shop has a pack:
        _ = shop.pack
    }

    @Test func sameSeedSameRoll() {
        var r1 = SeededRandomNumberGenerator(seed: 7)
        var r2 = SeededRandomNumberGenerator(seed: 7)
        let s1 = ShopRoller.rollShop(unlocked: .all, currentTable: 1, rng: &r1)
        let s2 = ShopRoller.rollShop(unlocked: .all, currentTable: 1, rng: &r2)
        #expect(s1 == s2)
    }

    @Test func rerollCostEscalates() {
        var rng = SeededRandomNumberGenerator(seed: 1)
        let s0 = ShopRoller.rollShop(unlocked: .all, currentTable: 1, rng: &rng, rerollsUsed: 0)
        let s2 = ShopRoller.rollShop(unlocked: .all, currentTable: 1, rng: &rng, rerollsUsed: 2)
        #expect(s2.rerollCost > s0.rerollCost)
    }
}

@Suite("Shop — booster packs")
struct BoosterPackTests {

    @Test func charmSmallPackContents() {
        var rng = SeededRandomNumberGenerator(seed: 11)
        let pack = ShopRoller.openPack(.charmSmall, unlocked: .all, currentTable: 1, rng: &rng)
        #expect(pack.charms.count == 3)
        #expect(pack.pickCount == 1)
    }

    @Test func charmLargePackPicksTwo() {
        var rng = SeededRandomNumberGenerator(seed: 11)
        let pack = ShopRoller.openPack(.charmLarge, unlocked: .all, currentTable: 1, rng: &rng)
        #expect(pack.charms.count == 5)
        #expect(pack.pickCount == 2)
    }

    @Test func spellPackFiltersByMinTable() {
        var rng = SeededRandomNumberGenerator(seed: 11)
        // Currently on Table 1 — Charleston Whisper (T5+) and Joker's Gift (T3+) excluded.
        let pack = ShopRoller.openPack(.spellSmall, unlocked: .all, currentTable: 1, rng: &rng)
        for spell in pack.spells {
            #expect(spell.minTable <= 1)
        }
    }

    @Test func spellPackUnlocksHigherTablesAtT5() {
        var rng = SeededRandomNumberGenerator(seed: 11)
        let pack = ShopRoller.openPack(.spellMega, unlocked: .all, currentTable: 5, rng: &rng)
        // Some T5+ spells may now appear (Charleston Whisper).
        // Just sanity-check: every spell has minTable ≤ 5.
        for spell in pack.spells {
            #expect(spell.minTable <= 5)
        }
    }

    @Test func mixedPackHasAllThreeTypes() {
        var rng = SeededRandomNumberGenerator(seed: 11)
        let pack = ShopRoller.openPack(.mixed, unlocked: .all, currentTable: 1, rng: &rng)
        #expect(!pack.charms.isEmpty)
        #expect(!pack.constellations.isEmpty)
        #expect(!pack.spells.isEmpty)
        #expect(pack.pickCount == 3)
    }

    @Test func packPricesMatchDesignDoc() {
        #expect(BoosterPack.charmSmall.price == 4)
        #expect(BoosterPack.charmLarge.price == 7)
        #expect(BoosterPack.constellation.price == 4)
        #expect(BoosterPack.spellSmall.price == 3)
        #expect(BoosterPack.spellMega.price == 6)
        #expect(BoosterPack.mixed.price == 10)
    }
}

@Suite("Charm catalog")
struct CharmCatalogTests {

    @Test func hasFifteenStarterCharms() {
        #expect(CharmCatalog.starter.count == 15)
    }

    @Test func eachCharmHasUniqueId() {
        let ids = CharmCatalog.starter.map(\.id)
        #expect(Set(ids).count == ids.count)
    }

    @Test func legendaryCharmsExist() {
        let legendary = CharmCatalog.charms(by: .legendary)
        #expect(!legendary.isEmpty)
    }
}

@Suite("Constellation catalog")
struct ConstellationCatalogTests {

    @Test func hasEightStarterConstellations() {
        #expect(ConstellationCatalog.starter.count == 8)
    }

    @Test func dracoBoostsQingHeavily() {
        let draco = ConstellationCatalog.constellation(id: "draco")!
        if case .pattern(let p) = draco.target {
            #expect(p == .qingYiSe)
        } else {
            Issue.record("Draco should target a pattern")
        }
        #expect(draco.baseDelta == 30)
        #expect(draco.multDelta == 1.5)
    }
}

@Suite("Spell catalog")
struct SpellCatalogTests {

    @Test func hasTwelveStarterSpells() {
        #expect(SpellCatalog.starter.count == 12)
    }

    @Test func charlestonWhisperGatedToT5() {
        let s = SpellCatalog.spell(id: "charleston_whisper")!
        #expect(s.minTable == 5)
    }

    @Test func availableSpellsRespectTableGate() {
        let t1 = SpellCatalog.available(forTable: 1).map(\.id)
        let t5 = SpellCatalog.available(forTable: 5).map(\.id)
        #expect(!t1.contains("charleston_whisper"))
        #expect(t5.contains("charleston_whisper"))
    }
}
