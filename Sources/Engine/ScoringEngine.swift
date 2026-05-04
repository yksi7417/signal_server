/// Per-event entry in a scoring breakdown — useful for UI reveal animations.
public struct ScoreEvent: Codable, Sendable, Hashable {
    public let label: String
    public let baseDelta: Int
    public let multDelta: Double
    public let multFactor: Double      // multiplicative multiplier (× factor)

    public init(label: String, baseDelta: Int = 0, multDelta: Double = 0, multFactor: Double = 1.0) {
        self.label = label
        self.baseDelta = baseDelta
        self.multDelta = multDelta
        self.multFactor = multFactor
    }
}

/// Final score for a hand: faan (for win-threshold), base × mult (for coins).
public struct ScoringResult: Codable, Sendable, Hashable {
    public let faan: Int
    public let base: Int
    public let mult: Double
    public let total: Int            // base × mult, rounded
    public let events: [ScoreEvent]
    public let primaryPattern: Pattern?
}

/// Inputs to the scoring engine.
public struct ScoringInputs: Sendable {
    public var hand: Hand
    public var seatWind: Wind
    public var prevailingWind: Wind
    public var selfDrawn: Bool
    public var charms: [Charm]
    public var patternBumps: [Pattern: PatternBumps]
    public var spellsUsedThisRun: Int
    public var bonusBaseBumpFromConstellations: Int  // Andromeda

    public init(
        hand: Hand,
        seatWind: Wind,
        prevailingWind: Wind,
        selfDrawn: Bool,
        charms: [Charm] = [],
        patternBumps: [Pattern: PatternBumps] = [:],
        spellsUsedThisRun: Int = 0,
        bonusBaseBumpFromConstellations: Int = 0
    ) {
        self.hand = hand
        self.seatWind = seatWind
        self.prevailingWind = prevailingWind
        self.selfDrawn = selfDrawn
        self.charms = charms
        self.patternBumps = patternBumps
        self.spellsUsedThisRun = spellsUsedThisRun
        self.bonusBaseBumpFromConstellations = bonusBaseBumpFromConstellations
    }
}

/// Computes final score (base × mult) for a winning hand using:
///   - Pattern level (base + mult, with constellation bumps)
///   - Charm effects (additive base, additive/multiplicative mult)
///   - Bonus tile contributions (with Andromeda boost)
///   - Self-drawn / seat-wind faan add-ons (also count as base bumps)
///
/// If the hand isn't winning, returns a zero `ScoringResult`.
public enum ScoringEngine {

    public static func score(_ inputs: ScoringInputs) -> ScoringResult {
        let hand = inputs.hand
        guard HandValidator.isWinning(hand) else {
            return ScoringResult(faan: 0, base: 0, mult: 0, total: 0, events: [], primaryPattern: nil)
        }

        var events: [ScoreEvent] = []
        var base = 0
        var mult = 0.0

        // 1. Find best decomposition (max faan).
        let decomps = HandValidator.decompositions(of: hand.playTiles)
        let scored = decomps.map { (decomp: $0, patterns: PatternDetector.patterns(in: $0)) }
        // Pick decomposition that maximises pattern-faan total (tiebreak by 清一色 over 混一色).
        let pick = scored.max { lhs, rhs in
            faanSum(of: lhs.patterns) < faanSum(of: rhs.patterns)
        } ?? scored.first!
        let decomp = pick.decomp
        var patterns = pick.patterns
        if patterns.contains(.qingYiSe) { patterns.remove(.hunYiSe) }

        // Faan total for win-threshold gating.
        var faanTotal = patterns.reduce(0) { $0 + FaanCalculator.faan(for: $1) }

        // Faan add-ons (bonus tile + self-drawn).
        for tile in hand.bonus {
            if case .flower(let n) = tile, seatWind(forBonusIndex: n) == inputs.seatWind {
                faanTotal += 1
            }
            if case .season(let n) = tile, seatWind(forBonusIndex: n) == inputs.seatWind {
                faanTotal += 1
            }
        }
        if inputs.selfDrawn { faanTotal += 1 }

        // 2. Primary pattern: highest-faan; ties broken by canonical ordering.
        let primary: Pattern? = pickPrimary(patterns)
        if let primary {
            let bumps = inputs.patternBumps[primary] ?? PatternBumps()
            let baseLv = primary.baseLevel1 + bumps.baseDelta
            let multLv = primary.multLevel1 + bumps.multDelta
            base += baseLv
            mult += multLv
            events.append(.init(label: primary.chinese, baseDelta: baseLv, multDelta: multLv))
        }

        // 3. Per-meld base/mult bonuses (charms): pair, pung, kong, chow, dragons.
        let melds = decomp.allMelds
        for charm in inputs.charms {
            switch charm.effect {
            case .perPairBase(let amt):
                let pairs = melds.filter(\.isPair).count
                if pairs > 0 {
                    base += pairs * amt
                    events.append(.init(label: charm.name, baseDelta: pairs * amt))
                }
            case .perPungMult(let factor):
                let pungs = melds.filter { $0.isPung || $0.isKong }.count
                for _ in 0..<pungs {
                    mult *= factor
                }
                if pungs > 0 {
                    events.append(.init(label: "\(charm.name) ×\(pungs)", multFactor: factor))
                }
            case .perChowBase(let amt):
                let chows = melds.filter(\.isChow).count
                if chows > 0 {
                    base += chows * amt
                    events.append(.init(label: charm.name, baseDelta: chows * amt))
                }
            case .perDragonBase(let amt):
                let dragons = hand.playTiles.filter { if case .dragon = $0 { return true }; return false }.count
                if dragons > 0 {
                    base += dragons * amt
                    events.append(.init(label: charm.name, baseDelta: dragons * amt))
                }
            case .perTileSuitBase(let suit, let amt):
                let n = hand.playTiles.filter { $0.suit == suit }.count
                if n > 0 {
                    base += n * amt
                    events.append(.init(label: charm.name, baseDelta: n * amt))
                }
            case .suitMult(let suit, let factor):
                if hand.playTiles.contains(where: { $0.suit == suit }) {
                    mult *= factor
                    events.append(.init(label: charm.name, multFactor: factor))
                }
            case .windHandBase(let wind, let amt):
                if inputs.prevailingWind == wind {
                    base += amt
                    events.append(.init(label: charm.name, baseDelta: amt))
                }
            case .spellMultGrowth(let per):
                let bonus = Double(inputs.spellsUsedThisRun) * per
                if bonus > 0 {
                    mult += bonus
                    events.append(.init(label: "\(charm.name) +\(bonus)", multDelta: bonus))
                }
            case .coinsPerWin, .skipCharlestonBonus, .nextTableSweepMult:
                break // handled by Run/CoinCalculator, not scoring
            }
        }

        // 4. Bonus tile additive base (Andromeda + seat-wind +1 faan add-ons).
        if !hand.bonus.isEmpty {
            let perBonusBase = inputs.bonusBaseBumpFromConstellations
            // Constellation-driven base bump.
            if perBonusBase > 0 {
                let total = perBonusBase * hand.bonus.count
                base += total
                events.append(.init(label: "Andromeda", baseDelta: total))
            }
        }

        // 5. Seat-wind matching bonus tiles → +5 base each (small flat),
        //    primarily reflected in faan; we already counted the +1 faan above.
        for tile in hand.bonus {
            switch tile {
            case .flower(let n) where seatWind(forBonusIndex: n) == inputs.seatWind:
                base += 5
                events.append(.init(label: "Flower-\(inputs.seatWind.english)", baseDelta: 5))
            case .season(let n) where seatWind(forBonusIndex: n) == inputs.seatWind:
                base += 5
                events.append(.init(label: "Season-\(inputs.seatWind.english)", baseDelta: 5))
            default: break
            }
        }

        // 6. Self-drawn small base bonus (in addition to faan).
        if inputs.selfDrawn {
            base += 5
            events.append(.init(label: "Self-Drawn", baseDelta: 5))
        }

        // Guard against degenerate zero-mult (e.g. honor-only fluke).
        if mult <= 0 { mult = 1.0 }

        let total = Int((Double(base) * mult).rounded())
        return ScoringResult(faan: faanTotal, base: base, mult: mult, total: total, events: events, primaryPattern: primary)
    }

    // MARK: - Helpers

    private static func faanSum(of patterns: Set<Pattern>) -> Int {
        // For decomposition picking, prefer patterns with higher faan.
        // 清一色 shadows 混一色 if both are claimed.
        var p = patterns
        if p.contains(.qingYiSe) { p.remove(.hunYiSe) }
        return p.reduce(0) { $0 + FaanCalculator.faan(for: $1) }
    }

    private static func pickPrimary(_ patterns: Set<Pattern>) -> Pattern? {
        var p = patterns
        if p.contains(.qingYiSe) { p.remove(.hunYiSe) }
        // Highest-faan-first canonical order.
        for pattern in [Pattern.qingYiSe, .hunYiSe, .duiDui, .ping] where p.contains(pattern) {
            return pattern
        }
        return nil
    }
}
