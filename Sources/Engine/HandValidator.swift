/// Validates whether a set of tiles is a winning mahjong hand and enumerates
/// every distinct decomposition into 1 pair + sets of three.
///
/// MVP scope:
/// - Standard structure: exactly 1 pair + N sets of 3, where N ≥ 1.
/// - Sets are pungs (3 of a kind) or chows (3 sequential same-suit).
/// - Honor tiles (winds/dragons) can only form pair/pung — never chow.
/// - Kongs are not searched for here (T3+ feature). Pre-declared kongs in
///   `Hand.melds` are not honored yet either.
public enum HandValidator {

    /// All distinct decompositions of `tiles` into 1 pair + sets of 3.
    /// Returns an empty array when no valid decomposition exists.
    public static func decompositions(of tiles: [Tile]) -> [HandDecomposition] {
        // Bonus tiles never participate in a decomposition.
        let inPlay = tiles.filter { !$0.isBonus }

        // Total tiles must be 2 + 3*N for some N ≥ 0.
        guard inPlay.count >= 2, (inPlay.count - 2) % 3 == 0 else { return [] }
        let setsNeeded = (inPlay.count - 2) / 3

        var counts: [Tile: Int] = [:]
        for t in inPlay { counts[t, default: 0] += 1 }

        // Try every tile that has ≥ 2 copies as the pair.
        var results: [HandDecomposition] = []
        for (tile, count) in counts where count >= 2 {
            var withoutPair = counts
            withoutPair[tile] = count - 2
            let setSearch = findSets(in: withoutPair, remaining: setsNeeded)
            for sets in setSearch {
                results.append(HandDecomposition(pair: tile, sets: sets))
            }
        }
        return results
    }

    /// True if `tiles` decompose into at least one valid winning structure.
    public static func isWinning(tiles: [Tile]) -> Bool {
        !decompositions(of: tiles).isEmpty
    }

    /// Convenience for `Hand`. Considers `playTiles` (concealed + meld tiles).
    public static func isWinning(_ hand: Hand) -> Bool {
        isWinning(tiles: hand.playTiles)
    }

    // MARK: - Recursive set search

    private static func findSets(in counts: [Tile: Int], remaining: Int) -> [[Meld]] {
        // Base case: no more sets needed; remaining tiles must all be 0.
        if remaining == 0 {
            return counts.values.allSatisfy({ $0 == 0 }) ? [[]] : []
        }

        // Pick the smallest tile with count > 0. By always extracting from the
        // smallest tile we avoid generating permuted duplicates of the same
        // decomposition.
        let candidates = counts.filter { $0.value > 0 }.keys.sorted()
        guard let next = candidates.first else { return [] }

        var results: [[Meld]] = []

        // Option 1: pung (3 identical).
        if (counts[next] ?? 0) >= 3 {
            var c = counts
            c[next]! -= 3
            for sub in findSets(in: c, remaining: remaining - 1) {
                results.append([.pung(next)] + sub)
            }
        }

        // Option 2: chow (3 sequential same-suit). Only for suited tiles
        // with rank 1–7 and the next two ranks present.
        if let suit = next.suit, let rank = next.rank, rank <= 7 {
            let mid = Tile.suited(suit, rank: rank + 1)
            let hi  = Tile.suited(suit, rank: rank + 2)
            if (counts[mid] ?? 0) >= 1 && (counts[hi] ?? 0) >= 1 {
                var c = counts
                c[next]! -= 1
                c[mid]! -= 1
                c[hi]!  -= 1
                for sub in findSets(in: c, remaining: remaining - 1) {
                    results.append([.chow(suit, low: rank)] + sub)
                }
            }
        }

        return results
    }
}
