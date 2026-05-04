/// A Spell is a one-shot tactical effect (Balatro's Tarot card renamed).
/// Up to 2 in the consumable slot (shared with Constellations).
public struct Spell: Codable, Sendable, Hashable, Identifiable {
    public let id: String
    public let name: String
    public let description: String
    public let minTable: Int            // gates by Table; 1 = always available
    public let effect: SpellEffect

    public init(
        id: String,
        name: String,
        description: String,
        minTable: Int = 1,
        effect: SpellEffect
    ) {
        self.id = id
        self.name = name
        self.description = description
        self.minTable = minTable
        self.effect = effect
    }
}

/// Concrete spell behaviors. Some are gated by Table (e.g. Charleston Whisper
/// is T5+) and remain inert in MVP — they appear in shop pools but cannot
/// be used.
public enum SpellEffect: Codable, Sendable, Hashable {
    /// Swap one tile in hand with the top of the wall.
    case swapWithWall
    /// Peek at the opponent's next 3 discards.
    case revealOpponentDiscards(count: Int)
    /// Add an extra Charleston pass (T5+).
    case extraCharlestonPass
    /// Transform one tile into another tile of the same suit.
    case transformTileSameSuit
    /// Add an in-tile Joker to your hand (T3+).
    case addJoker
    /// Convert one tile into a Dragon.
    case convertToDragon
    /// Discard your full hand and redraw.
    case resetHand
    /// Change the prevailing wind for this hand.
    case shiftPrevailingWind
    /// Double the base score of the next pattern you complete.
    case doubleNextPatternBase
    /// Force-draw a Flower or Season tile from the bonus deck.
    case forceBonusDraw
    /// Opponent skips their next discard call.
    case opponentSkipNextCall
    /// Add 30s to the turn timer (Boss hands only — UI-side).
    case addTurnTimer(seconds: Int)
}

public enum SpellCatalog {

    public static let starter: [Spell] = [
        Spell(id: "the_swap", name: "The Swap",
              description: "Exchange one tile in hand with the top of the wall.",
              effect: .swapWithWall),
        Spell(id: "the_reveal", name: "The Reveal",
              description: "Peek at the opponent's next 3 discards.",
              effect: .revealOpponentDiscards(count: 3)),
        Spell(id: "charleston_whisper", name: "The Charleston Whisper",
              description: "Get one extra Charleston pass. (T5+)",
              minTable: 5,
              effect: .extraCharlestonPass),
        Spell(id: "tile_transformation", name: "Tile Transformation",
              description: "Turn one tile into any other tile of the same suit.",
              effect: .transformTileSameSuit),
        Spell(id: "jokers_gift", name: "Joker's Gift",
              description: "Add a Joker tile to your hand. (T3+)",
              minTable: 3,
              effect: .addJoker),
        Spell(id: "dragons_favor", name: "Dragon's Favor",
              description: "Convert one tile into a Dragon.",
              effect: .convertToDragon),
        Spell(id: "the_reset", name: "The Reset",
              description: "Discard your full hand, redraw.",
              effect: .resetHand),
        Spell(id: "wind_shift", name: "Wind Shift",
              description: "Change the prevailing wind for this hand.",
              effect: .shiftPrevailingWind),
        Spell(id: "double_down", name: "Double Down",
              description: "Double the base score of the next pattern you complete.",
              effect: .doubleNextPatternBase),
        Spell(id: "flower_bloom", name: "Flower Bloom",
              description: "Force-draw a Flower or Season tile.",
              effect: .forceBonusDraw),
        Spell(id: "the_hush", name: "The Hush",
              description: "Opponent skips their next discard call.",
              effect: .opponentSkipNextCall),
        Spell(id: "time_slow", name: "Time Slow",
              description: "Add 30 seconds to turn timer. (Boss hands only)",
              effect: .addTurnTimer(seconds: 30)),
    ]

    public static func spell(id: String) -> Spell? {
        starter.first(where: { $0.id == id })
    }

    /// Spells available given the current Table number.
    public static func available(forTable table: Int) -> [Spell] {
        starter.filter { $0.minTable <= table }
    }
}
