// Renders the placeholder Mahjong+× app icon to a 1024×1024 PNG.
// One-shot: run `swift run icon-gen path/to/AppIcon-1024.png`. The Xcode
// asset catalog reads it from there. Replace with a commissioned icon
// before public release.

import Foundation
import CoreGraphics
import CoreText
import ImageIO
import UniformTypeIdentifiers
import AppKit

let outputPath: String
if CommandLine.arguments.count >= 2 {
    outputPath = CommandLine.arguments[1]
} else {
    outputPath = "App/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png"
}

let size = 1024
let width = size
let height = size

// Palm Beach palette — same tokens as Theme.swift.
let lanai      = CGColor(red: 0xFA/255, green: 0xF6/255, blue: 0xEE/255, alpha: 1)
let wicker     = CGColor(red: 0xE8/255, green: 0xDD/255, blue: 0xC9/255, alpha: 1)
let goldDeep   = CGColor(red: 0x8C/255, green: 0x6A/255, blue: 0x1F/255, alpha: 1)
let gold       = CGColor(red: 0xC9/255, green: 0xA2/255, blue: 0x4A/255, alpha: 1)
let windInk    = CGColor(red: 0x2B/255, green: 0x3A/255, blue: 0x4A/255, alpha: 1)

guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB),
      let ctx = CGContext(
        data: nil,
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: 0,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
      )
else {
    fputs("Failed to make CGContext\n", stderr)
    exit(1)
}

// Background — soft linen.
ctx.setFillColor(lanai)
ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))

// Decorative gold ring (subtle Palm Beach accent).
ctx.setStrokeColor(gold)
ctx.setLineWidth(8)
let inset: CGFloat = 64
ctx.strokeEllipse(in: CGRect(x: inset, y: inset, width: CGFloat(width) - 2*inset, height: CGFloat(height) - 2*inset))

// Inner wicker disk for contrast against the title.
ctx.setFillColor(wicker.copy(alpha: 0.45)!)
let diskInset: CGFloat = 130
ctx.fillEllipse(in: CGRect(x: diskInset, y: diskInset, width: CGFloat(width) - 2*diskInset, height: CGFloat(height) - 2*diskInset))

/// Helper that draws an attributed line centered horizontally at `centerY`.
func drawCenteredLine(_ string: String, font: CTFont, color: CGColor, centerY: CGFloat) {
    let attrs: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: NSColor(cgColor: color)!,
    ]
    let attributed = NSAttributedString(string: string, attributes: attrs)
    let line = CTLineCreateWithAttributedString(attributed)
    // CTLineGetImageBounds uses ctx.textPosition; reset before measuring.
    ctx.textPosition = .zero
    let bounds = CTLineGetImageBounds(line, ctx)
    let x = (CGFloat(width) - bounds.width) / 2 - bounds.origin.x
    let y = centerY - bounds.height / 2 - bounds.origin.y
    ctx.textPosition = CGPoint(x: x, y: y)
    CTLineDraw(line, ctx)
}

// Title "Mahjong" in deep ink, large serif italic across the upper area.
drawCenteredLine(
    "Mahjong",
    font: CTFontCreateWithName("Georgia-Italic" as CFString, 180, nil),
    color: windInk,
    centerY: CGFloat(height) * 0.58
)

// Subtitle "+ ×" — the brand mark — in deep gold beneath.
drawCenteredLine(
    "+  ×",
    font: CTFontCreateWithName("Georgia-Bold" as CFString, 280, nil),
    color: goldDeep,
    centerY: CGFloat(height) * 0.30
)

guard let image = ctx.makeImage() else {
    fputs("Failed to render image\n", stderr); exit(1)
}

let url = URL(fileURLWithPath: outputPath)
try? FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)

guard let dest = CGImageDestinationCreateWithURL(url as CFURL, UTType.png.identifier as CFString, 1, nil) else {
    fputs("Failed to make destination at \(outputPath)\n", stderr); exit(1)
}
CGImageDestinationAddImage(dest, image, nil)
guard CGImageDestinationFinalize(dest) else {
    fputs("Failed to write PNG\n", stderr); exit(1)
}
print("Wrote \(outputPath)")
