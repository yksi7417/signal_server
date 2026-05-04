public enum Wind: String, CaseIterable, Codable, Sendable, Hashable {
    case east   // 東
    case south  // 南
    case west   // 西
    case north  // 北

    public var chinese: String {
        switch self {
        case .east:  return "東"
        case .south: return "南"
        case .west:  return "西"
        case .north: return "北"
        }
    }

    public var english: String {
        switch self {
        case .east:  return "East"
        case .south: return "South"
        case .west:  return "West"
        case .north: return "North"
        }
    }

    /// Display label used throughout the UI: "東 East"
    public var label: String { "\(chinese) \(english)" }

    /// Turn order around the table: East → South → West → North → East …
    public var next: Wind {
        switch self {
        case .east:  return .south
        case .south: return .west
        case .west:  return .north
        case .north: return .east
        }
    }
}
