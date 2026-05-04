import Testing
@testable import Engine

@Suite("HandEngine — dealing")
struct HandEngineDealingTests {

    @Test func dealsHandSizeTilesPerSeat() {
        var rng = SeededRandomNumberGenerator(seed: 1)
        let cfg = HandConfig(table: 1, handIndex: 1, prevailingWind: .east, handSize: 4)
        let state = HandState.deal(config: cfg, wallTiles: TileSet.table1Hand1(), rng: &rng)
        for seat in Seat.allCases {
            #expect(state.hand(for: seat).concealed.count == 4)
        }
        #expect(state.phase == .awaitingDraw(.player))
    }

    @Test func dealIsDeterministicWithSeed() {
        let cfg = HandConfig(table: 1, handIndex: 1, prevailingWind: .east, handSize: 4)
        var rng1 = SeededRandomNumberGenerator(seed: 99)
        var rng2 = SeededRandomNumberGenerator(seed: 99)
        let s1 = HandState.deal(config: cfg, wallTiles: TileSet.table1Hand1(), rng: &rng1)
        let s2 = HandState.deal(config: cfg, wallTiles: TileSet.table1Hand1(), rng: &rng2)
        #expect(s1.hands == s2.hands)
    }
}

@Suite("HandEngine — turn flow")
struct HandEngineTurnFlowTests {

    private func freshState(seed: UInt64 = 7, handSize: Int = 4) -> HandState {
        var rng = SeededRandomNumberGenerator(seed: seed)
        let cfg = HandConfig(table: 1, handIndex: 1, prevailingWind: .east, handSize: handSize)
        return HandState.deal(config: cfg, wallTiles: TileSet.table1Hand1(), rng: &rng)
    }

    @Test func drawAdvancesToDiscardPhase() throws {
        var s = freshState()
        try HandEngine.apply(.draw(.player), to: &s)
        if case .awaitingDiscardOrWin(let seat) = s.phase {
            #expect(seat == .player)
        } else {
            Issue.record("expected awaitingDiscardOrWin, got \(s.phase)")
        }
        #expect(s.hand(for: .player).concealed.count == 5)
    }

    @Test func discardReducesHandAndAdvancesTurn() throws {
        var s = freshState()
        try HandEngine.apply(.draw(.player), to: &s)
        let toss = s.hand(for: .player).concealed.first!
        try HandEngine.apply(.discard(.player, toss), to: &s)
        #expect(s.hand(for: .player).concealed.count == 4)
        #expect(s.discards.count == 1)
        #expect(s.discards.first?.tile == toss)
        // No claim opportunity (random tile, AI not winning), so turn passes to AI.
        #expect(s.phase == .awaitingDraw(.ai))
    }

    @Test func cannotDiscardOutOfTurn() throws {
        var s = freshState()
        try HandEngine.apply(.draw(.player), to: &s)
        let toss = s.hand(for: .player).concealed.first!
        do {
            try HandEngine.apply(.discard(.ai, toss), to: &s)
            Issue.record("expected wrongPhase")
        } catch HandActionError.wrongPhase {
            // ok
        }
    }

    @Test func cannotDiscardTileNotInHand() throws {
        var s = freshState()
        try HandEngine.apply(.draw(.player), to: &s)
        let bogus = Tile.dragon(.red)   // not in cookies-only Table 1 H1
        do {
            try HandEngine.apply(.discard(.player, bogus), to: &s)
            Issue.record("expected tileNotInHand")
        } catch HandActionError.tileNotInHand {
            // ok
        }
    }

    @Test func wallExhaustionEndsHand() throws {
        // Wall has exactly 8 tiles — both seats deal, then wall is empty,
        // and the very first draw exhausts.
        let smallWall = Array(TileSet.table1Hand1().prefix(8))
        let cfg = HandConfig(table: 1, handIndex: 1, prevailingWind: .east, handSize: 4)
        var s = HandState.deal(config: cfg, wall: Wall(tiles: smallWall))
        #expect(s.wall.isEmpty)
        do {
            try HandEngine.apply(.draw(.player), to: &s)
            Issue.record("expected wallExhausted")
        } catch HandActionError.wallExhausted {
            // expected
        }
        #expect(s.outcome == .wallExhausted)
        #expect(s.phase == .ended)
    }
}

@Suite("HandEngine — winning")
struct HandEngineWinningTests {

    /// Rigged wall: player gets 4 cookies that are 1-1-1-7, then draws a 7
    /// to complete pung+pair; AI gets junk; remaining is junk.
    private func riggedWinWall() -> [Tile] {
        // Player sees these in order (first 4 deal slots): 1,1,1,7
        // AI sees next 4: 2,3,4,5
        // Then draw pile: 7 (player wins on first draw)
        let dealt: [Tile] = [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 7),  // player
            .suited(.cookies, rank: 2), .suited(.cookies, rank: 3),
            .suited(.cookies, rank: 4), .suited(.cookies, rank: 5),  // ai
            .suited(.cookies, rank: 7),                              // player draws -> wins
        ]
        // Pad to a reasonable length
        let pad: [Tile] = (1...20).map { _ in .suited(.cookies, rank: 8) }
        return dealt + pad
    }

    @Test func selfDrawnWinIsLegalAndScored() throws {
        let cfg = HandConfig(table: 1, handIndex: 1, prevailingWind: .east, handSize: 4)
        var s = HandState.deal(config: cfg, wall: Wall(tiles: riggedWinWall()))
        // Sanity: player has 1,1,1,7 (sorted)
        #expect(s.hand(for: .player).concealed == [
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 1), .suited(.cookies, rank: 7),
        ])
        try HandEngine.apply(.draw(.player), to: &s)
        // Now player has 1,1,1,7,7 — winning.
        let legal = HandEngine.legalActions(in: s)
        #expect(legal.contains(.declareWin(.player, fromDiscard: false)))
        try HandEngine.apply(.declareWin(.player, fromDiscard: false), to: &s)
        #expect(s.phase == .ended)
        if case .win(let seat, let score, let from) = s.outcome {
            #expect(seat == .player)
            #expect(from == nil)
            #expect(score.faan > 0)
        } else {
            Issue.record("expected win outcome, got \(String(describing: s.outcome))")
        }
    }

    @Test func minFaanEnforced() throws {
        // Same wall, but config requires faan ≥ 100 (impossible).
        let cfg = HandConfig(
            table: 2, handIndex: 4, prevailingWind: .north,
            handSize: 4, minFaanToWin: 100
        )
        var s = HandState.deal(config: cfg, wall: Wall(tiles: riggedWinWall()))
        try HandEngine.apply(.draw(.player), to: &s)
        // Win is not in legal actions due to faan threshold.
        let legal = HandEngine.legalActions(in: s)
        #expect(!legal.contains(.declareWin(.player, fromDiscard: false)))
        // Trying to force the win still fails.
        do {
            try HandEngine.apply(.declareWin(.player, fromDiscard: false), to: &s)
            Issue.record("expected faanBelowMinimum")
        } catch HandActionError.faanBelowMinimum {
            // expected
        }
    }
}
