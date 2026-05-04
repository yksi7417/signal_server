import Testing
@testable import Engine

@Suite("Standard tile set composition")
struct TileSetTests {

    @Test func standardSetTotalCount() {
        #expect(TileSet.standard().count == 144)
    }

    @Test func standardSetSuitedCounts() {
        let set = TileSet.standard()
        for suit in Suit.allCases {
            for rank in 1...9 {
                let count = set.filter { $0 == .suited(suit, rank: rank) }.count
                #expect(count == 4, "expected 4 of \(rank)\(suit.chinese), got \(count)")
            }
        }
    }

    @Test func standardSetWindCounts() {
        let set = TileSet.standard()
        for wind in Wind.allCases {
            let count = set.filter { $0 == .wind(wind) }.count
            #expect(count == 4, "expected 4 of \(wind.label), got \(count)")
        }
    }

    @Test func standardSetDragonCounts() {
        let set = TileSet.standard()
        for dragon in Dragon.allCases {
            let count = set.filter { $0 == .dragon(dragon) }.count
            #expect(count == 4, "expected 4 of \(dragon.english), got \(count)")
        }
    }

    @Test func standardSetBonusTilesAreSingletons() {
        let set = TileSet.standard()
        for n in 1...4 {
            #expect(set.filter { $0 == .flower(n) }.count == 1)
            #expect(set.filter { $0 == .season(n) }.count == 1)
        }
    }

    @Test func standardSetHasNoJokers() {
        #expect(!TileSet.standard().contains(.joker))
    }

    // MARK: - Table 1 Hand 1

    @Test func table1Hand1HasOnlyCookies() {
        let set = TileSet.table1Hand1()
        #expect(set.count == 36)
        #expect(set.allSatisfy { $0.suit == .cookies })
    }

    @Test func table1Hand1HasFourOfEachRank() {
        let set = TileSet.table1Hand1()
        for rank in 1...9 {
            let count = set.filter { $0 == .suited(.cookies, rank: rank) }.count
            #expect(count == 4)
        }
    }
}
