import Testing
@testable import Engine

@Suite("Pattern detector")
struct PatternDetectorTests {

    // MARK: - 對對 Dui Dui (all pungs/kongs, no chows)

    @Test func duiDuiAllPungs() {
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.bamboo, rank: 5), .suited(.bamboo, rank: 5), .suited(.bamboo, rank: 5),
            .dragon(.red), .dragon(.red),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(patterns.contains(.duiDui))
        #expect(!patterns.contains(.ping))
    }

    @Test func duiDuiHonorsOnly() {
        let tiles: [Tile] = [
            .wind(.east), .wind(.east), .wind(.east),
            .dragon(.red), .dragon(.red),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(patterns.contains(.duiDui))
    }

    @Test func notDuiDuiWhenChowsPresent() {
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 2), .suited(.cookies, rank: 3),
            .suited(.cookies, rank: 7), .suited(.cookies, rank: 7),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(!patterns.contains(.duiDui))
    }

    // MARK: - 平 Ping (all chows, one number suit, no honors)

    @Test func pingAllChows() {
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 2), .suited(.cookies, rank: 3),
            .suited(.cookies, rank: 6), .suited(.cookies, rank: 7), .suited(.cookies, rank: 8),
            .suited(.cookies, rank: 9), .suited(.cookies, rank: 9),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(patterns.contains(.ping))
        #expect(patterns.contains(.qingYiSe))   // pure one suit
        #expect(!patterns.contains(.duiDui))
    }

    @Test func pingSingleChowAtT1() {
        // 5-tile T1 hand: chow + pair
        let tiles: [Tile] = [
            .suited(.cookies, rank: 3),
            .suited(.cookies, rank: 4),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 9),
            .suited(.cookies, rank: 9),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(patterns.contains(.ping))
        #expect(patterns.contains(.qingYiSe))
    }

    @Test func notPingWhenPungPresent() {
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 5),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(!patterns.contains(.ping))
        #expect(patterns.contains(.duiDui))
    }

    // MARK: - 清一色 Qing Yi Se (pure one suit, no honors)

    @Test func qingYiSeChowsOnly() {
        let tiles: [Tile] = [
            .suited(.bamboo, rank: 1), .suited(.bamboo, rank: 2), .suited(.bamboo, rank: 3),
            .suited(.bamboo, rank: 4), .suited(.bamboo, rank: 5), .suited(.bamboo, rank: 6),
            .suited(.bamboo, rank: 9), .suited(.bamboo, rank: 9),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(patterns.contains(.qingYiSe))
        #expect(patterns.contains(.ping))
        #expect(!patterns.contains(.hunYiSe))
    }

    @Test func qingYiSePungsOnly() {
        let tiles: [Tile] = [
            .suited(.characters, rank: 1), .suited(.characters, rank: 1), .suited(.characters, rank: 1),
            .suited(.characters, rank: 5), .suited(.characters, rank: 5), .suited(.characters, rank: 5),
            .suited(.characters, rank: 9), .suited(.characters, rank: 9),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(patterns.contains(.qingYiSe))
        #expect(patterns.contains(.duiDui))
    }

    @Test func notQingYiSeWithMultipleSuits() {
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.bamboo, rank: 5), .suited(.bamboo, rank: 5), .suited(.bamboo, rank: 5),
            .dragon(.red), .dragon(.red),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(!patterns.contains(.qingYiSe))
        #expect(!patterns.contains(.hunYiSe))   // multiple suits, not a pure-one
    }

    // MARK: - 混一色 Hun Yi Se (one suit + honors)

    @Test func hunYiSe() {
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 5), .suited(.cookies, rank: 6), .suited(.cookies, rank: 7),
            .dragon(.red), .dragon(.red),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(patterns.contains(.hunYiSe))
        #expect(!patterns.contains(.qingYiSe))
    }

    @Test func qingYiSeAndHunYiSeMutuallyExclusive() {
        // pure cookies — qing only.
        let pureTiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 9), .suited(.cookies, rank: 9),
        ]
        let p1 = PatternDetector.patterns(in: Hand(concealed: pureTiles))
        #expect(p1.contains(.qingYiSe))
        #expect(!p1.contains(.hunYiSe))

        // cookies + dragons — hun only.
        let mixedTiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .dragon(.red), .dragon(.red),
        ]
        let p2 = PatternDetector.patterns(in: Hand(concealed: mixedTiles))
        #expect(p2.contains(.hunYiSe))
        #expect(!p2.contains(.qingYiSe))
    }

    // MARK: - Combinations

    @Test func duiDuiQingYiSeCombo() {
        // All pungs, all one suit, no honors → 對對 + 清一色
        let tiles: [Tile] = [
            .suited(.bamboo, rank: 2), .suited(.bamboo, rank: 2), .suited(.bamboo, rank: 2),
            .suited(.bamboo, rank: 5), .suited(.bamboo, rank: 5), .suited(.bamboo, rank: 5),
            .suited(.bamboo, rank: 9), .suited(.bamboo, rank: 9),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(patterns.contains(.duiDui))
        #expect(patterns.contains(.qingYiSe))
        #expect(!patterns.contains(.ping))      // pings need chows
        #expect(!patterns.contains(.hunYiSe))
    }

    @Test func pingQingYiSeCombo() {
        // All chows, one suit → 平 + 清一色
        let tiles: [Tile] = [
            .suited(.characters, rank: 1), .suited(.characters, rank: 2), .suited(.characters, rank: 3),
            .suited(.characters, rank: 4), .suited(.characters, rank: 5), .suited(.characters, rank: 6),
            .suited(.characters, rank: 9), .suited(.characters, rank: 9),
        ]
        let patterns = PatternDetector.patterns(in: Hand(concealed: tiles))
        #expect(patterns.contains(.ping))
        #expect(patterns.contains(.qingYiSe))
    }
}
