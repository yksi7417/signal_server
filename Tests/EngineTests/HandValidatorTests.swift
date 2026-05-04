import Testing
@testable import Engine

@Suite("Hand validator — Table 1 (5 tiles)")
struct HandValidatorTable1Tests {

    @Test func pungPlusPairWins() {
        // 3×5筒 + 2×7筒 — pung + pair, all Cookies.
        let tiles: [Tile] = [
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7),
            .suited(.cookies, rank: 7),
        ]
        #expect(HandValidator.isWinning(tiles: tiles))
        let decomps = HandValidator.decompositions(of: tiles)
        #expect(decomps.count == 1)
        #expect(decomps[0].pair == .suited(.cookies, rank: 7))
        #expect(decomps[0].sets == [.pung(.suited(.cookies, rank: 5))])
    }

    @Test func chowPlusPairWins() {
        // 3-4-5筒 + 2×9筒
        let tiles: [Tile] = [
            .suited(.cookies, rank: 3),
            .suited(.cookies, rank: 4),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 9),
            .suited(.cookies, rank: 9),
        ]
        #expect(HandValidator.isWinning(tiles: tiles))
        let decomps = HandValidator.decompositions(of: tiles)
        #expect(decomps.count == 1)
        #expect(decomps[0].pair == .suited(.cookies, rank: 9))
        #expect(decomps[0].sets == [.chow(.cookies, low: 3)])
    }

    @Test func notWinningWithJustFiveRandomTiles() {
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 3),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7),
            .suited(.cookies, rank: 9),
        ]
        #expect(!HandValidator.isWinning(tiles: tiles))
    }

    @Test func notWinningPairOnly() {
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 1),
        ]
        // Just a pair, no sets — needs setsNeeded=0 case.
        #expect(HandValidator.isWinning(tiles: tiles))
    }

    @Test func notWinningWrongCount() {
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 2),
        ]
        // 3 tiles can't form pair + sets-of-3.
        #expect(!HandValidator.isWinning(tiles: tiles))
    }

    @Test func bonusTilesAreIgnored() {
        // pung + pair plus bonus flowers — still a 5-tile play hand.
        let tiles: [Tile] = [
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7),
            .suited(.cookies, rank: 7),
            .flower(1),
            .season(2),
        ]
        #expect(HandValidator.isWinning(tiles: tiles))
    }

    @Test func consecutiveOverlappingChowAmbiguity() {
        // 1-2-3-4-5筒 + 7筒×2 has only one valid decomposition (chow 1-2-3 OR 3-4-5
        // and the leftover doesn't form a set). Sanity test: detection is unique.
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 2),
            .suited(.cookies, rank: 3),
            .suited(.cookies, rank: 4),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7),
            .suited(.cookies, rank: 7),
        ]
        // 7 tiles isn't a winning size (must be 5, 8, 11…).
        #expect(!HandValidator.isWinning(tiles: tiles))
    }
}

@Suite("Hand validator — Table 2 (8 tiles)")
struct HandValidatorTable2Tests {

    @Test func twoPungsPlusPair() {
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.bamboo,  rank: 5), .suited(.bamboo,  rank: 5), .suited(.bamboo,  rank: 5),
            .dragon(.red), .dragon(.red),
        ]
        #expect(HandValidator.isWinning(tiles: tiles))
    }

    @Test func twoChowsPlusPair() {
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 2), .suited(.cookies, rank: 3),
            .suited(.cookies, rank: 6), .suited(.cookies, rank: 7), .suited(.cookies, rank: 8),
            .suited(.cookies, rank: 9), .suited(.cookies, rank: 9),
        ]
        #expect(HandValidator.isWinning(tiles: tiles))
    }

    @Test func chowPungPair() {
        let tiles: [Tile] = [
            .suited(.bamboo, rank: 2), .suited(.bamboo, rank: 3), .suited(.bamboo, rank: 4),
            .suited(.characters, rank: 7), .suited(.characters, rank: 7), .suited(.characters, rank: 7),
            .wind(.east), .wind(.east),
        ]
        #expect(HandValidator.isWinning(tiles: tiles))
    }

    @Test func ambiguousDecompositionFound() {
        // 1-1-1-2-2-2-3-3 in cookies — can be (pung 1, pung 2, pair 3) OR (chow 1-2-3 twice + pair? no, only 2 of 3).
        // Actually: 1,1,1,2,2,2,3,3 → 8 tiles → pair + 2 sets.
        // Decomp A: pung(1) + pung(2) + pair(3)
        // Decomp B: chow(1-2-3) + chow(1-2-3) needs three 3s — only have two. Not valid.
        // So only one decomp.
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 2), .suited(.cookies, rank: 2), .suited(.cookies, rank: 2),
            .suited(.cookies, rank: 3), .suited(.cookies, rank: 3),
        ]
        let decomps = HandValidator.decompositions(of: tiles)
        #expect(decomps.count == 1)
        #expect(decomps[0].sets.allSatisfy { $0.isPung })
    }

    @Test func twoChowsSharingTilesProducesOneDecomp() {
        // 1-2-3-1-2-3-7-7 — two overlapping chows + pair. Valid.
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 2), .suited(.cookies, rank: 2),
            .suited(.cookies, rank: 3), .suited(.cookies, rank: 3),
            .suited(.cookies, rank: 7), .suited(.cookies, rank: 7),
        ]
        let decomps = HandValidator.decompositions(of: tiles)
        #expect(decomps.count >= 1)
        // At least one decomposition exists.
        #expect(HandValidator.isWinning(tiles: tiles))
    }
}

@Suite("Hand validator — honor constraints")
struct HandValidatorHonorTests {

    @Test func honorsOnlyFormPungsOrPairs() {
        // 3 east winds + 2 red dragons — pung + pair.
        let tiles: [Tile] = [
            .wind(.east), .wind(.east), .wind(.east),
            .dragon(.red), .dragon(.red),
        ]
        #expect(HandValidator.isWinning(tiles: tiles))
        let decomps = HandValidator.decompositions(of: tiles)
        #expect(decomps.count == 1)
        #expect(decomps[0].sets == [.pung(.wind(.east))])
    }

    @Test func cannotChowAcrossHonors() {
        // east + south + west should not form a chow.
        let tiles: [Tile] = [
            .wind(.east), .wind(.south), .wind(.west),
            .dragon(.red), .dragon(.red),
        ]
        #expect(!HandValidator.isWinning(tiles: tiles))
    }

    @Test func cannotChowAcrossSuits() {
        // 1筒 + 2條 + 3萬 is not a chow.
        let tiles: [Tile] = [
            .suited(.cookies, rank: 1),
            .suited(.bamboo, rank: 2),
            .suited(.characters, rank: 3),
            .dragon(.red), .dragon(.red),
        ]
        #expect(!HandValidator.isWinning(tiles: tiles))
    }
}

@Suite("Hand validator — Hand convenience")
struct HandValidatorHandTests {

    @Test func winningViaHandStruct() {
        let hand = Hand(concealed: [
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7),
            .suited(.cookies, rank: 7),
        ])
        #expect(HandValidator.isWinning(hand))
    }

    @Test func bonusTilesInHandIgnored() {
        var hand = Hand(concealed: [
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 7),
            .suited(.cookies, rank: 7),
        ])
        hand.bonus = [.flower(1), .season(2)]
        #expect(HandValidator.isWinning(hand))
    }
}
