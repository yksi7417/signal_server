// swift-tools-version: 6.1
import PackageDescription

let package = Package(
    name: "MahjongPlusX",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        .library(name: "Engine", targets: ["Engine"]),
        .executable(name: "mahjong-plusx-sim", targets: ["MahjongPlusXSim"]),
    ],
    targets: [
        .target(name: "Engine"),
        .executableTarget(
            name: "MahjongPlusXSim",
            dependencies: ["Engine"]
        ),
        .testTarget(name: "EngineTests", dependencies: ["Engine"]),
    ]
)
