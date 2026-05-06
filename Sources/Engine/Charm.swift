/// A Charm is a permanent run modifier (Balatro's "Joker" renamed for the
/// mahjong vocabulary clash with in-tile wild "jokers"). Up to 5 active.
public struct Charm: Codable, Sendable, Hashable, Identifiable {
    public let id: String
    public let name: String
    public let rarity: Rarity
    public let description: String
    public let effect: CharmEffect

    public init(
        id: String,
        name: String,
        rarity: Rarity,
        description: String,
        effect: CharmEffect
    ) {
        self.id = id
        self.name = name
        self.rarity = rarity
        self.description = description
        self.effect = effect
    }

    public enum Rarity: String, Codable, Sendable, Hashable, CaseIterable {
        case common, uncommon, rare, legendary
    }
}

/// Concrete charm effects used by the scoring engine.
///
/// The 15 starter charms from the design doc map onto these cases. New
/// charms can extend the enum as the pool grows.
public enum CharmEffect: Codable, Sendable, Hashable {
    /// +N base on hands whose prevailing wind matches.
    case windHandBase(wind: Wind, amount: Int)
    /// Any tile of the given suit in winning hand: × factor mult (applied once).
    case suitMult(suit: Suit, factor: Double)
    /// +N base for each tile of the given suit in winning hand.
    case perTileSuitBase(suit: Suit, amount: Int)
    /// +N base per dragon tile in winning hand.
    case perDragonBase(amount: Int)
    /// +N base per pair scored.
    case perPairBase(amount: Int)
    /// × factor mult per pung/kong scored.
    case perPungMult(factor: Double)
    /// +N base per chow scored.
    case perChowBase(amount: Int)
    /// Each spell used permanently grows mult by `per` (handled by the run, not scoring).
    case spellMultGrowth(per: Double)
    /// +N coins per hand won (post-scoring).
    case coinsPerWin(amount: Int)
    /// One-shot bonus that activates if the player skips Charleston (T5+).
    /// Inert in MVP since Charleston is post-MVP.
    case skipCharlestonBonus(amount: Int)
    /// Multiplier applied on the first hand of the next Table after a sweep.
    case nextTableSweepMult(factor: Double)
    /// UI-only: reveal the opponent's concealed hand. No scoring effect;
    /// the iOS layer reads `Run.charms` and renders accordingly.
    case revealOpponentHand
}

extension Charm {
    /// True if this charm has the reveal-opponent-hand effect ("Crystal Lens").
    public var revealsOpponentHand: Bool {
        if case .revealOpponentHand = effect { return true }
        return false
    }
}
