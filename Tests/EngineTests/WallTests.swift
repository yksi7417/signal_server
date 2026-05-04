import Testing
@testable import Engine

@Suite("Wall")
struct WallTests {

    @Test func remainingDecrementsOnDraw() {
        var w = Wall(tiles: [.suited(.cookies, rank: 1), .suited(.cookies, rank: 2)])
        #expect(w.remaining == 2)
        _ = w.draw()
        #expect(w.remaining == 1)
        _ = w.draw()
        #expect(w.remaining == 0)
        #expect(w.isEmpty)
    }

    @Test func drawReturnsNilWhenEmpty() {
        var w = Wall(tiles: [])
        #expect(w.draw() == nil)
    }

    @Test func bulkDrawTakesUpToRequested() {
        var w = Wall(tiles: TileSet.table1Hand1())
        let first4 = w.draw(4)
        #expect(first4.count == 4)
        #expect(w.remaining == 32)
    }

    @Test func shuffleIsDeterministicWithSeed() {
        var rng1 = SeededRandomNumberGenerator(seed: 42)
        var rng2 = SeededRandomNumberGenerator(seed: 42)
        let w1 = Wall.shuffled(TileSet.standard(), using: &rng1)
        let w2 = Wall.shuffled(TileSet.standard(), using: &rng2)
        #expect(w1.tiles == w2.tiles)
    }

    @Test func differentSeedsProduceDifferentShuffles() {
        var rng1 = SeededRandomNumberGenerator(seed: 1)
        var rng2 = SeededRandomNumberGenerator(seed: 2)
        let w1 = Wall.shuffled(TileSet.standard(), using: &rng1)
        let w2 = Wall.shuffled(TileSet.standard(), using: &rng2)
        #expect(w1.tiles != w2.tiles)
    }
}
