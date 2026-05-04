public enum Suit: String, CaseIterable, Codable, Sendable, Hashable {
    case cookies     // 筒 (dots)
    case bamboo      // 條 (sticks)
    case characters  // 萬 (cracks)

    public var chinese: String {
        switch self {
        case .cookies:    return "筒"
        case .bamboo:     return "條"
        case .characters: return "萬"
        }
    }

    public var english: String {
        switch self {
        case .cookies:    return "Cookies"
        case .bamboo:     return "Bamboo"
        case .characters: return "Characters"
        }
    }
}
