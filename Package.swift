// swift-tools-version: 6.1
import PackageDescription

let package = Package(
    name: "MahjongPlusX",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        .library(name: "Engine", targets: ["Engine"]),
    ],
    targets: [
        .target(name: "Engine"),
        .testTarget(name: "EngineTests", dependencies: ["Engine"]),
    ]
)
