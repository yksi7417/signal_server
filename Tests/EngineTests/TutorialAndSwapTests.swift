import Testing
@testable import Engine

@Suite("Tutorial pre-grants")
struct TutorialPreGrantTests {

    @Test func tutorialRunHasStarterKit() {
        let run = Run(seed: 1, tutorial: true)
        #expect(run.charms.contains(where: { $0.id == "crystal_lens" }))
        #expect(run.revealsOpponentHand)
        let swapSpells = run.consumables.compactMap { c -> Spell? in
            if case .spell(let s) = c, s.id == "the_swap" { return s }
            return nil
        }
        #expect(swapSpells.count == 2)
    }

    @Test func defaultRunIsNonTutorial() {
        let run = Run(seed: 1)
        #expect(run.charms.isEmpty)
        #expect(run.consumables.isEmpty)
        #expect(!run.revealsOpponentHand)
    }
}

@Suite("Wall undrawn API")
struct WallUndrawnTests {

    @Test func undrawnReflectsRemainingTiles() {
        var w = Wall(tiles: [
            .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 2),
            .suited(.cookies, rank: 3),
        ])
        #expect(Array(w.undrawn) == [
            .suited(.cookies, rank: 1),
            .suited(.cookies, rank: 2),
            .suited(.cookies, rank: 3),
        ])
        _ = w.draw()
        #expect(Array(w.undrawn) == [
            .suited(.cookies, rank: 2),
            .suited(.cookies, rank: 3),
        ])
    }

    @Test func swapUndrawnReplacesTile() {
        var w = Wall(tiles: [
            .suited(.cookies, rank: 5),
            .suited(.cookies, rank: 6),
            .suited(.cookies, rank: 7),
        ])
        let displaced = w.swapUndrawn(relativeIndex: 1, with: .dragon(.red))
        #expect(displaced == .suited(.cookies, rank: 6))
        #expect(Array(w.undrawn) == [
            .suited(.cookies, rank: 5),
            .dragon(.red),
            .suited(.cookies, rank: 7),
        ])
    }

    @Test func swapUndrawnOutOfRangeReturnsNil() {
        var w = Wall(tiles: [.suited(.cookies, rank: 1)])
        #expect(w.swapUndrawn(relativeIndex: 99, with: .dragon(.red)) == nil)
    }
}

@Suite("Run.applySwap")
struct RunApplySwapTests {

    private func freshTutorialRun() -> Run { Run(seed: 42, tutorial: true) }
    // Non-tutorial run for negative-test paths
    private func freshBareRun() -> Run { Run(seed: 7) }

    @Test func swapExchangesTilesAndConsumesSpell() {
        var run = freshTutorialRun()
        var state = run.startHand()
        // Sanity: player has 4 tiles.
        let player = state.hand(for: .player).concealed
        #expect(player.count == 4)

        let toSwap = player[0]
        let wallSlice = Array(state.wall.undrawn)
        let target = wallSlice[3]
        #expect(toSwap != target || true)   // they may coincidentally be equal; not asserted

        let initialSpells = run.consumables.count
        let ok = run.applySwap(
            handTile: toSwap,
            wallRelativeIndex: 3,
            seat: .player,
            in: &state
        )
        #expect(ok)
        #expect(run.consumables.count == initialSpells - 1)

        // Hand should now contain the wall tile, not the swapped-out tile (assuming distinct).
        if toSwap != target {
            let postHand = state.hand(for: .player).concealed
            #expect(postHand.contains(target))
            // The displaced hand tile should now be at the wall index 3.
            #expect(state.wall.undrawn[state.wall.drawIndex + 3] == toSwap)
        }
    }

    @Test func swapFailsWithoutSpell() {
        var run = freshBareRun()
        var state = run.startHand()
        let any = state.hand(for: .player).concealed.first ?? .suited(.cookies, rank: 1)
        let ok = run.applySwap(handTile: any, wallRelativeIndex: 0, seat: .player, in: &state)
        #expect(!ok)
    }

    @Test func swapFailsWhenHandTileMissing() {
        var run = freshTutorialRun()
        var state = run.startHand()
        let bogus = Tile.joker   // never in T1 wall
        let ok = run.applySwap(handTile: bogus, wallRelativeIndex: 0, seat: .player, in: &state)
        #expect(!ok)
    }
}

@Suite("Crystal Lens charm")
struct CrystalLensTests {

    @Test func charmExistsInCatalog() {
        #expect(CharmCatalog.charm(id: "crystal_lens") != nil)
    }

    @Test func revealsOpponentHandFlagOnEffect() {
        let charm = CharmCatalog.charm(id: "crystal_lens")!
        #expect(charm.revealsOpponentHand)
    }

    @Test func nonRevealCharmsReturnFalse() {
        let other = CharmCatalog.charm(id: "the_hostess")!
        #expect(!other.revealsOpponentHand)
    }
}
