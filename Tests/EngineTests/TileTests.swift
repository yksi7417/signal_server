import Testing
@testable import Engine

@Suite("Tile vocabulary")
struct TileTests {

    // MARK: - Equality & hashing

    @Test func suitedTileEquality() {
        #expect(Tile.suited(.cookies, rank: 5) == Tile.suited(.cookies, rank: 5))
        #expect(Tile.suited(.cookies, rank: 5) != Tile.suited(.cookies, rank: 6))
        #expect(Tile.suited(.cookies, rank: 5) != Tile.suited(.bamboo, rank: 5))
    }

    @Test func honorAndBonusEquality() {
        #expect(Tile.wind(.east) == Tile.wind(.east))
        #expect(Tile.wind(.east) != Tile.wind(.south))
        #expect(Tile.dragon(.red) == Tile.dragon(.red))
        #expect(Tile.flower(2) == Tile.flower(2))
        #expect(Tile.flower(2) != Tile.season(2))
    }

    // MARK: - Classification

    @Test func isSuited() {
        #expect(Tile.suited(.bamboo, rank: 3).isSuited)
        #expect(!Tile.wind(.north).isSuited)
        #expect(!Tile.dragon(.white).isSuited)
        #expect(!Tile.flower(1).isSuited)
        #expect(!Tile.joker.isSuited)
    }

    @Test func isHonor() {
        #expect(Tile.wind(.east).isHonor)
        #expect(Tile.dragon(.green).isHonor)
        #expect(!Tile.suited(.cookies, rank: 1).isHonor)
        #expect(!Tile.flower(1).isHonor)
        #expect(!Tile.season(1).isHonor)
    }

    @Test func isBonus() {
        #expect(Tile.flower(3).isBonus)
        #expect(Tile.season(1).isBonus)
        #expect(!Tile.wind(.east).isBonus)
        #expect(!Tile.suited(.bamboo, rank: 9).isBonus)
    }

    @Test func suitAndRankAccessors() {
        let tile = Tile.suited(.characters, rank: 7)
        #expect(tile.suit == .characters)
        #expect(tile.rank == 7)
        #expect(Tile.wind(.east).suit == nil)
        #expect(Tile.dragon(.red).rank == nil)
    }

    // MARK: - Display

    @Test func suitChineseLabels() {
        #expect(Suit.cookies.chinese == "筒")
        #expect(Suit.bamboo.chinese == "條")
        #expect(Suit.characters.chinese == "萬")
    }

    @Test func windLabels() {
        #expect(Wind.east.label == "東 East")
        #expect(Wind.south.label == "南 South")
        #expect(Wind.west.label == "西 West")
        #expect(Wind.north.label == "北 North")
    }

    @Test func windRotation() {
        #expect(Wind.east.next == .south)
        #expect(Wind.south.next == .west)
        #expect(Wind.west.next == .north)
        #expect(Wind.north.next == .east)
    }

    @Test func dragonLabels() {
        #expect(Dragon.red.chinese == "中")
        #expect(Dragon.green.chinese == "發")
        #expect(Dragon.white.chinese == "白")
    }

    @Test func tileDescription() {
        #expect(Tile.suited(.bamboo, rank: 5).description == "5條")
        #expect(Tile.wind(.east).description == "東")
        #expect(Tile.dragon(.red).description == "中")
        #expect(Tile.flower(2).description == "F2")
        #expect(Tile.season(3).description == "S3")
        #expect(Tile.joker.description == "J")
    }
}
