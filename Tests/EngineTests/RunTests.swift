import Testing
@testable import Engine

@Suite("Run — initialization")
struct RunInitTests {

    @Test func startsAtTable1Hand1WithZeroCoins() {
        let run = Run(seed: 42)
        #expect(run.table == 1)
        #expect(run.handIndex == 1)
        #expect(run.coins == 0)
        #expect(run.charms.isEmpty)
        #expect(run.consumables.isEmpty)
        #expect(run.status == .inProgress)
    }

    @Test func slotsArePerDesignDoc() {
        #expect(Run.slots.charms == 5)
        #expect(Run.slots.consumables == 2)
    }

    @Test func currentHandConfigForT1H1() {
        var run = Run(seed: 1)
        let cfg = run.currentHandConfig()
        #expect(cfg.table == 1)
        #expect(cfg.handIndex == 1)
        #expect(cfg.handSize == 4)
        #expect(cfg.minFaanToWin == 0)
        #expect(cfg.prevailingWind == .east)
        #expect(cfg.bossModifier == nil)
    }

    @Test func currentHandConfigForT2H4Boss() {
        var run = Run(seed: 1)
        run.table = 2
        run.handIndex = 4
        let cfg = run.currentHandConfig()
        #expect(cfg.handSize == 7)
        #expect(cfg.minFaanToWin == 1)
        #expect(cfg.prevailingWind == .north)
        #expect(cfg.bossModifier != nil)
    }
}

@Suite("Run — inventory")
struct RunInventoryTests {

    @Test func canAddUpToFiveCharms() {
        var run = Run(seed: 1)
        for charm in CharmCatalog.starter.prefix(5) {
            let added = run.addCharm(charm)
            #expect(added)
        }
        #expect(!run.canAddCharm)
        let extra = run.addCharm(CharmCatalog.starter[5])
        #expect(!extra)
        #expect(run.charms.count == 5)
    }

    @Test func cannotDoubleAddSameCharmId() {
        var run = Run(seed: 1)
        let cookie = CharmCatalog.charm(id: "cookie_jar")!
        let firstAdd = run.addCharm(cookie)
        let secondAdd = run.addCharm(cookie)
        #expect(firstAdd)
        #expect(!secondAdd)
        #expect(run.charms.count == 1)
    }

    @Test func canAddUpToTwoConsumables() {
        var run = Run(seed: 1)
        let s1 = Consumable.spell(SpellCatalog.spell(id: "the_swap")!)
        let s2 = Consumable.constellation(ConstellationCatalog.constellation(id: "orion")!)
        let s3 = Consumable.spell(SpellCatalog.spell(id: "the_reset")!)
        let a1 = run.addConsumable(s1)
        let a2 = run.addConsumable(s2)
        let a3 = run.addConsumable(s3)
        #expect(a1)
        #expect(a2)
        #expect(!run.canAddConsumable)
        #expect(!a3)
    }

    @Test func usingConstellationAppliesBumps() {
        var run = Run(seed: 1)
        let orion = ConstellationCatalog.constellation(id: "orion")!
        _ = run.addConsumable(.constellation(orion))
        let used = run.useConsumable(id: "c:orion")
        #expect(used)
        let bumps = run.patternBumps[.duiDui]!
        #expect(bumps.baseDelta == 10)
        #expect(bumps.multDelta == 0.5)
        #expect(run.consumables.isEmpty)
    }

    @Test func pleiadesBumpsAllPatterns() {
        var run = Run(seed: 1)
        let pleiades = ConstellationCatalog.constellation(id: "pleiades")!
        _ = run.addConsumable(.constellation(pleiades))
        _ = run.useConsumable(id: "c:pleiades")
        for p in Pattern.allCases {
            let b = run.patternBumps[p]!
            #expect(b.baseDelta == 5)
            #expect(b.multDelta == 0.2)
        }
    }

    @Test func andromedaBumpsBonusBase() {
        var run = Run(seed: 1)
        let andromeda = ConstellationCatalog.constellation(id: "andromeda")!
        _ = run.addConsumable(.constellation(andromeda))
        _ = run.useConsumable(id: "c:andromeda")
        #expect(run.bonusBaseBumpFromConstellations == 10)
    }

    @Test func usingSpellIncrementsSpellCount() {
        var run = Run(seed: 1)
        let swap = SpellCatalog.spell(id: "the_swap")!
        _ = run.addConsumable(.spell(swap))
        _ = run.useConsumable(id: "s:the_swap")
        #expect(run.stats.spellsUsed == 1)
        #expect(run.consumables.isEmpty)
    }
}

@Suite("Run — table progression")
struct RunProgressionTests {

    @Test func advanceMovesThroughTable1() {
        var run = Run(seed: 1)
        // Hand 1 → Hand 2
        run.advance()
        #expect(run.handIndex == 2)
        #expect(run.table == 1)
        // Hand 2 → 3 → 4 (boss)
        run.advance(); run.advance()
        #expect(run.handIndex == 4)
        // Boss → next Table requires currentTable.isComplete
        // Manually mark table complete by adjusting handsLost.
        run.currentTable.handsLost = 4
        run.advance()
        #expect(run.table == 2)
        #expect(run.handIndex == 1)
    }

    @Test func sweepingTableTriggersBonus() {
        var run = Run(seed: 1)
        run.currentTable.handsWon = 4
        run.advance()
        #expect(run.coins == CoinCalculator.tableSweepBonus)
        #expect(run.stats.tableSweepCount == 1)
    }

    @Test func completingMVPRunMarksRunComplete() {
        var run = Run(seed: 1)
        run.table = 2
        run.handIndex = 4
        run.currentTable.handsWon = 4
        run.advance()
        #expect(run.status == .completed)
    }
}

@Suite("Run — recordHandOutcome")
struct RunOutcomeTests {

    @Test func playerWinIncrementsStatsAndCoins() {
        var run = Run(seed: 1)
        _ = run.addCharm(CharmCatalog.charm(id: "the_hostess")!)
        let cfg = TableProgression.handConfig(table: 1, hand: 1)
        let hand = Hand(concealed: [
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7),
            .suited(.cookies, rank: 7),
        ])
        let s = HandState(
            config: cfg,
            hands: [hand, Hand()],
            wall: Wall(tiles: []),
            phase: .ended,
            outcome: .win(seat: .player, score: FaanScore(faan: 5, reasons: []), fromDiscard: nil)
        )
        let initialCoins = run.coins
        run.recordHandOutcome(s)
        // 5 faan × 5 coin/faan + 5 from Hostess = 30
        #expect(run.coins == initialCoins + 30)
        #expect(run.stats.handsWon == 1)
        #expect(run.handIndex == 2)
    }
}

@Suite("Run — frozen suit boss modifier")
struct RunFrozenSuitTests {

    @Test func frozenSuitBlocksSelfDrawnWin() throws {
        // T2 H4 boss with frozen cookies — winning cookies hand must be rejected.
        let cfg = HandConfig(
            table: 2, handIndex: 4, prevailingWind: .north,
            handSize: 7, minFaanToWin: 1,
            bossModifier: .frozenSuit(.cookies)
        )
        let winningHand: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 6), .suited(.cookies, rank: 7),
            .suited(.cookies, rank: 9),    // 7 in hand; will draw 9th to win on 8th
        ]
        let walltiles = winningHand + [.suited(.cookies, rank: 9)] + (0..<10).map { _ in Tile.suited(.bamboo, rank: 1) }
        // Build a state with the winning hand pre-set, draw a 9 to complete pair.
        var hands = [Hand(concealed: winningHand), Hand(concealed: Array(repeating: .suited(.bamboo, rank: 5), count: 7))]
        // Move to awaitingDiscardOrWin: simulate that player drew 9.
        hands[0].concealed.append(.suited(.cookies, rank: 9))
        hands[0].concealed.sort()
        var state = HandState(
            config: cfg,
            hands: hands,
            wall: Wall(tiles: walltiles),
            phase: .awaitingDiscardOrWin(.player)
        )
        // Expect not winning due to frozen cookies.
        let legal = HandEngine.legalActions(in: state)
        #expect(!legal.contains(.declareWin(.player, fromDiscard: false)))
        do {
            try HandEngine.apply(.declareWin(.player, fromDiscard: false), to: &state)
            Issue.record("expected frozen-suit to block win")
        } catch HandActionError.notWinning {
            // ok
        }
    }
}
