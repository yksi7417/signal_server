/// Given a winning decomposition, determine which scoring patterns it satisfies.
public enum PatternDetector {

    /// Patterns satisfied by a single decomposition.
    ///
    /// Note: 混一色 and 清一色 are mutually exclusive (清一色 requires no
    /// honors, 混一色 requires honors). The detector returns whichever fits.
    public static func patterns(in decomp: HandDecomposition) -> Set<Pattern> {
        var found: Set<Pattern> = []

        // Decomposition's tiles excluding bonus (decomp doesn't include bonus).
        let allTiles = decomp.allMelds.flatMap(\.tiles)
        let suits = Set(allTiles.compactMap(\.suit))
        let hasHonors = allTiles.contains(where: \.isHonor)

        // 對對 — every set is a pung/kong (no chows). Pair is always there.
        let allPungish = decomp.sets.allSatisfy { $0.isPung || $0.isKong }
        if allPungish {
            found.insert(.duiDui)
        }

        // 平 — every set is a chow, all in one number suit, no honors.
        let allChows = !decomp.sets.isEmpty && decomp.sets.allSatisfy(\.isChow)
        if allChows && !hasHonors && suits.count == 1 {
            found.insert(.ping)
        }

        // 清一色 — exactly one number suit, no honors at all.
        if !hasHonors && suits.count == 1 {
            found.insert(.qingYiSe)
        }

        // 混一色 — exactly one number suit + honors.
        if hasHonors && suits.count == 1 {
            found.insert(.hunYiSe)
        }

        // Honor-only edge case (no number suits, all honors): treat as 對對 only.
        // This naturally falls out — no other pattern matches.

        return found
    }

    /// Best-pattern set across all decompositions of a winning hand.
    /// Returns the union; the scorer picks the best combination.
    public static func patterns(in hand: Hand) -> Set<Pattern> {
        var union: Set<Pattern> = []
        for d in HandValidator.decompositions(of: hand.playTiles) {
            union.formUnion(patterns(in: d))
        }
        return union
    }
}
