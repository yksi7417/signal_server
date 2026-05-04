import Testing
@testable import Engine

@Suite("Faan scoring — single patterns")
struct FaanScoringSinglePatternTests {

    private func hand(_ tiles: [Tile], bonus: [Tile] = []) -> Hand {
        var h = Hand(concealed: tiles)
        h.bonus = bonus
        return h
    }

    private var ctx: ScoringContext {
        ScoringContext(seatWind: .east, selfDrawn: false)
    }

    @Test func pingScoresOne() {
        let h = hand([
            .suited(.cookies, rank: 3), .suited(.cookies, rank: 4), .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 9), .suited(.cookies, rank: 9),
        ])
        let s = FaanCalculator.score(hand: h, context: ctx)
        // Ping (1) + Qing Yi Se (4) = 5
        #expect(s.faan == 5)
        #expect(s.reasons.contains(where: { $0.label == "平" && $0.faan == 1 }))
        #expect(s.reasons.contains(where: { $0.label == "清一色" && $0.faan == 4 }))
    }

    @Test func duiDuiScoresOne() {
        let h = hand([
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 5), .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7), .suited(.cookies, rank: 7),
        ])
        let s = FaanCalculator.score(hand: h, context: ctx)
        // Dui Dui (1) + Qing Yi Se (4) = 5
        #expect(s.faan == 5)
        #expect(s.reasons.contains(where: { $0.label == "對對" && $0.faan == 1 }))
        #expect(s.reasons.contains(where: { $0.label == "清一色" && $0.faan == 4 }))
    }

    @Test func hunYiSeScoresTwo() {
        let h = hand([
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 6), .suited(.cookies, rank: 7),
            .dragon(.red), .dragon(.red),
        ])
        let s = FaanCalculator.score(hand: h, context: ctx)
        // Hun Yi Se (2) only; not Dui Dui (chow present), not Ping (pung present), not Qing (honors).
        #expect(s.faan == 2)
        #expect(s.reasons.contains(where: { $0.label == "混一色" && $0.faan == 2 }))
    }

    @Test func qingYiSeScoresFour() {
        let h = hand([
            .suited(.bamboo, rank: 1), .suited(.bamboo, rank: 2), .suited(.bamboo, rank: 3),
            .suited(.bamboo, rank: 5), .suited(.bamboo, rank: 5), .suited(.bamboo, rank: 5),
            .suited(.bamboo, rank: 9), .suited(.bamboo, rank: 9),
        ])
        let s = FaanCalculator.score(hand: h, context: ctx)
        // Qing Yi Se (4) only; not Dui Dui (chow), not Ping (pung).
        #expect(s.faan == 4)
        #expect(s.reasons.contains(where: { $0.label == "清一色" && $0.faan == 4 }))
    }

    @Test func qingYiSeShadowsHunYiSe() {
        // Pure cookies — qing only, no hun.
        let h = hand([
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 9), .suited(.cookies, rank: 9),
        ])
        let s = FaanCalculator.score(hand: h, context: ctx)
        #expect(s.reasons.contains(where: { $0.label == "清一色" }))
        #expect(!s.reasons.contains(where: { $0.label == "混一色" }))
    }
}

@Suite("Faan scoring — bonus and combinations")
struct FaanScoringBonusTests {

    @Test func selfDrawnAddsOne() {
        let h = Hand(concealed: [
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 5), .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7), .suited(.cookies, rank: 7),
        ])
        let s = FaanCalculator.score(
            hand: h,
            context: ScoringContext(seatWind: .east, selfDrawn: true)
        )
        // Dui Dui (1) + Qing (4) + Self-Drawn (1) = 6
        #expect(s.faan == 6)
        #expect(s.reasons.contains(where: { $0.label == "Self-Drawn" }))
    }

    @Test func flowerMatchingSeatWindAddsOne() {
        var h = Hand(concealed: [
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 5), .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7), .suited(.cookies, rank: 7),
        ])
        h.bonus = [.flower(1)]   // East flower
        let s = FaanCalculator.score(
            hand: h,
            context: ScoringContext(seatWind: .east, selfDrawn: false)
        )
        // Dui Dui (1) + Qing (4) + Flower-East (1) = 6
        #expect(s.faan == 6)
        #expect(s.reasons.contains(where: { $0.label == "Flower-East" }))
    }

    @Test func flowerNotMatchingSeatWindNoBonus() {
        var h = Hand(concealed: [
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 5), .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7), .suited(.cookies, rank: 7),
        ])
        h.bonus = [.flower(2)]   // South flower
        let s = FaanCalculator.score(
            hand: h,
            context: ScoringContext(seatWind: .east, selfDrawn: false)
        )
        // Dui Dui (1) + Qing (4) = 5; flower doesn't match.
        #expect(s.faan == 5)
        #expect(!s.reasons.contains(where: { $0.label.contains("Flower") }))
    }

    @Test func seasonMatchingSeatWindAddsOne() {
        var h = Hand(concealed: [
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 5), .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7), .suited(.cookies, rank: 7),
        ])
        h.bonus = [.season(2)]   // South season
        let s = FaanCalculator.score(
            hand: h,
            context: ScoringContext(seatWind: .south, selfDrawn: false)
        )
        #expect(s.reasons.contains(where: { $0.label == "Season-South" }))
    }

    @Test func multipleBonusesStack() {
        var h = Hand(concealed: [
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 5), .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7), .suited(.cookies, rank: 7),
        ])
        h.bonus = [.flower(1), .season(1)]   // both East
        let s = FaanCalculator.score(
            hand: h,
            context: ScoringContext(seatWind: .east, selfDrawn: true)
        )
        // Dui Dui (1) + Qing (4) + Flower-East (1) + Season-East (1) + Self-Drawn (1) = 8
        #expect(s.faan == 8)
    }

    @Test func nonWinningHandScoresZero() {
        let h = Hand(concealed: [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 3),
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 7),
            .suited(.cookies, rank: 9),
        ])
        let s = FaanCalculator.score(
            hand: h,
            context: ScoringContext(seatWind: .east, selfDrawn: true)
        )
        #expect(s.faan == 0)
        #expect(s.reasons.isEmpty)
    }
}

@Suite("Coin calculator")
struct CoinCalculatorTests {

    @Test func zeroFaanZeroCoins() {
        let s = FaanScore(faan: 0, reasons: [])
        #expect(CoinCalculator.coins(for: s) == 0)
    }

    @Test func oneFaanFiveCoins() {
        let s = FaanScore(faan: 1, reasons: [])
        #expect(CoinCalculator.coins(for: s) == 5)
    }

    @Test func fourFaanTwentyCoins() {
        let s = FaanScore(faan: 4, reasons: [])
        #expect(CoinCalculator.coins(for: s) == 20)
    }

    @Test func tableSweepBonusOnlyWhenSwept() {
        #expect(CoinCalculator.tableCompletionBonus(swept: true) == 20)
        #expect(CoinCalculator.tableCompletionBonus(swept: false) == 0)
    }
}
