import SwiftUI

/// Palm Beach palette: wicker, lucite, linen, gold leaf, pastel tiles.
/// Locked in the design doc — golden hour on a lanai.
enum Theme {
    // Backgrounds
    static let lanai     = Color(hex: 0xFAF6EE)   // warm linen
    static let wicker    = Color(hex: 0xE8DDC9)   // beige wicker
    static let shadow    = Color(hex: 0xC9B895)   // muted golden shadow

    // Tile body / face
    static let tileFace  = Color(hex: 0xFCFAF3)   // creamy off-white
    static let tileBack  = Color(hex: 0xC9DDD3)   // soft jade for tile backs
    static let tileEdge  = Color(hex: 0xB6A47A)   // warm tan edge

    // Accents
    static let gold      = Color(hex: 0xC9A24A)   // gold leaf
    static let goldDeep  = Color(hex: 0x8C6A1F)
    static let coral     = Color(hex: 0xE08A6F)
    static let jade      = Color(hex: 0x6E9F87)
    static let plum      = Color(hex: 0x7C4D75)

    // Suit ink colors (subtle, on the tile face)
    static let cookies     = Color(hex: 0x4A7B6F)   // deep teal-green
    static let bamboo      = Color(hex: 0x4F6B2E)   // olive
    static let characters  = Color(hex: 0x8C2530)   // deep wine red

    // Honors
    static let dragonRed   = Color(hex: 0x8C2530)
    static let dragonGreen = Color(hex: 0x335E3F)
    static let dragonWhite = Color(hex: 0x808F92)
    static let windInk     = Color(hex: 0x2B3A4A)

    // Status / system
    static let win         = Color(hex: 0x6E9F87)
    static let loss        = Color(hex: 0xC15B5B)

    // Typography
    static let displayFont = "Georgia"
    static let bodyFont    = "Avenir-Medium"
}

extension Color {
    init(hex: UInt32) {
        let r = Double((hex >> 16) & 0xFF) / 255.0
        let g = Double((hex >> 8)  & 0xFF) / 255.0
        let b = Double(hex         & 0xFF) / 255.0
        self.init(red: r, green: g, blue: b)
    }
}
