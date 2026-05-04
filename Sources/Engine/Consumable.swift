/// A consumable (single-use) item — Constellation or Spell. Up to 2 in the
/// active slot per the design doc.
public enum Consumable: Codable, Sendable, Hashable, Identifiable {
    case constellation(Constellation)
    case spell(Spell)

    public var id: String {
        switch self {
        case .constellation(let c): return "c:\(c.id)"
        case .spell(let s):         return "s:\(s.id)"
        }
    }

    public var name: String {
        switch self {
        case .constellation(let c): return c.name
        case .spell(let s):         return s.name
        }
    }

    public var description: String {
        switch self {
        case .constellation(let c): return c.description
        case .spell(let s):         return s.description
        }
    }
}
