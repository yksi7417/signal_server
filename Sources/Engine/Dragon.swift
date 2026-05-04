public enum Dragon: String, CaseIterable, Codable, Sendable, Hashable {
    case red    // 中
    case green  // 發
    case white  // 白

    public var chinese: String {
        switch self {
        case .red:   return "中"
        case .green: return "發"
        case .white: return "白"
        }
    }

    public var english: String {
        switch self {
        case .red:   return "Red"
        case .green: return "Green"
        case .white: return "White"
        }
    }
}
