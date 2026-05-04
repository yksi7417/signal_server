import Testing
@testable import Engine

@Suite("ScoringEngine — base × mult")
struct ScoringEngineTests {

    private func winningCookies() -> Hand {
        // Pung 5 + pair 7 — qing yi se + dui dui in cookies (5 tiles, T1 hand).
        Hand(concealed: [
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7),
            .suited(.cookies, rank: 7),
        ])
    }

    @Test func qingYiSeAtLevelOne() {
        // Pure cookies pung+pair. Primary pattern = 清一色, base 80, mult 4.0.
        let hand = winningCookies()
        let inputs = ScoringInputs(
            hand: hand,
            seatWind: .east,
            prevailingWind: .east,
            selfDrawn: false
        )
        let r = ScoringEngine.score(inputs)
        // base = 80 (qing) + 5 (Flower-East? no bonus tiles) = 80
        // Wait — we don't have flower bonus, so just 80.
        // mult = 4.0
        // total = 80 * 4 = 320
        #expect(r.primaryPattern == .qingYiSe)
        #expect(r.base == 80)
        #expect(r.mult == 4.0)
        #expect(r.total == 320)
        #expect(r.faan >= 4)   // 清一色 = 4 faan minimum
    }

    @Test func cookieJarCharmTriplesMult() {
        let hand = winningCookies()
        let cookieJar = CharmCatalog.charm(id: "cookie_jar")!
        let inputs = ScoringInputs(
            hand: hand,
            seatWind: .east,
            prevailingWind: .east,
            selfDrawn: false,
            charms: [cookieJar]
        )
        let r = ScoringEngine.score(inputs)
        // mult = 4.0 × 3.0 = 12.0
        // total = 80 * 12 = 960
        #expect(r.mult == 12.0)
        #expect(r.total == 960)
    }

    @Test func windHandBaseAddsFlatBonus() {
        let hand = winningCookies()
        let eastWindCharm = CharmCatalog.charm(id: "east_wind_whisper")!
        let inputs = ScoringInputs(
            hand: hand,
            seatWind: .east,
            prevailingWind: .east,
            selfDrawn: false,
            charms: [eastWindCharm]
        )
        let r = ScoringEngine.score(inputs)
        // base = 80 + 10 = 90; mult = 4.0; total = 360
        #expect(r.base == 90)
        #expect(r.total == 360)
    }

    @Test func windHandBaseSkipsOnNonMatchingWind() {
        let hand = winningCookies()
        let eastWindCharm = CharmCatalog.charm(id: "east_wind_whisper")!
        let inputs = ScoringInputs(
            hand: hand,
            seatWind: .east,
            prevailingWind: .south,   // not East
            selfDrawn: false,
            charms: [eastWindCharm]
        )
        let r = ScoringEngine.score(inputs)
        #expect(r.base == 80)         // no bonus
    }

    @Test func perPungMultStacks() {
        let hand = Hand(concealed: [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 5), .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 9), .suited(.cookies, rank: 9),
        ])
        let pungPower = CharmCatalog.charm(id: "pung_power")!
        let inputs = ScoringInputs(
            hand: hand,
            seatWind: .east, prevailingWind: .east, selfDrawn: false,
            charms: [pungPower]
        )
        let r = ScoringEngine.score(inputs)
        // qing+duidui (primary qing). mult = 4.0 × 1.5 × 1.5 = 9.0 (2 pungs)
        #expect(r.primaryPattern == .qingYiSe)
        #expect(r.mult == 9.0)
    }

    @Test func selfDrawnAddsBaseAndFaan() {
        let hand = winningCookies()
        let inputs = ScoringInputs(
            hand: hand, seatWind: .east, prevailingWind: .east, selfDrawn: true
        )
        let r = ScoringEngine.score(inputs)
        // Self-drawn adds +5 base. base = 85. mult = 4. total = 340.
        #expect(r.base == 85)
        #expect(r.events.contains(where: { $0.label == "Self-Drawn" }))
    }

    @Test func nonWinningHandReturnsZero() {
        let hand = Hand(concealed: [
            .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 3),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7),
            .suited(.cookies, rank: 9),
        ])
        let inputs = ScoringInputs(
            hand: hand, seatWind: .east, prevailingWind: .east, selfDrawn: true
        )
        let r = ScoringEngine.score(inputs)
        #expect(r.total == 0)
        #expect(r.primaryPattern == nil)
    }

    @Test func patternBumpsRaiseBaseAndMult() {
        let hand = winningCookies()
        var bumps: [Pattern: PatternBumps] = [:]
        bumps[.qingYiSe] = PatternBumps(baseDelta: 30, multDelta: 1.5)   // Draco
        let inputs = ScoringInputs(
            hand: hand, seatWind: .east, prevailingWind: .east, selfDrawn: false,
            patternBumps: bumps
        )
        let r = ScoringEngine.score(inputs)
        // base = 80 + 30 = 110; mult = 4 + 1.5 = 5.5; total = 605
        #expect(r.base == 110)
        #expect(r.mult == 5.5)
        #expect(r.total == 605)
    }
}
