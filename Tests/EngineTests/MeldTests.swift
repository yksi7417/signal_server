import Testing
@testable import Engine

@Suite("Meld")
struct MeldTests {

    @Test func pairTiles() {
        let meld = Meld.pair(.suited(.cookies, rank: 5))
        #expect(meld.tiles == [.suited(.cookies, rank: 5), .suited(.cookies, rank: 5)])
        #expect(meld.isPair)
        #expect(!meld.isSet)
    }

    @Test func pungTiles() {
        let meld = Meld.pung(.dragon(.red))
        #expect(meld.tiles.count == 3)
        #expect(meld.tiles.allSatisfy { $0 == .dragon(.red) })
        #expect(meld.isPung)
        #expect(meld.isSet)
        #expect(meld.isHonorMeld)
    }

    @Test func kongTiles() {
        let meld = Meld.kong(.wind(.east), exposed: false)
        #expect(meld.tiles.count == 4)
        #expect(meld.isKong)
        #expect(meld.isSet)
        #expect(meld.isHonorMeld)
    }

    @Test func chowTiles() {
        let meld = Meld.chow(.bamboo, low: 3)
        #expect(meld.tiles == [
            .suited(.bamboo, rank: 3),
            .suited(.bamboo, rank: 4),
            .suited(.bamboo, rank: 5),
        ])
        #expect(meld.isChow)
        #expect(!meld.isHonorMeld)
        #expect(meld.suit == .bamboo)
    }

    @Test func meldSuit() {
        #expect(Meld.pung(.suited(.characters, rank: 1)).suit == .characters)
        #expect(Meld.pung(.wind(.south)).suit == nil)
        #expect(Meld.chow(.cookies, low: 1).suit == .cookies)
    }
}
