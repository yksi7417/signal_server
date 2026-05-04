/// Deterministic RNG used everywhere the engine needs randomness.
///
/// Implements xorshift64* — fast, good distribution for game-scale uses,
/// and reproducible from a 64-bit seed. Use this (or pass a fresh
/// `SystemRandomNumberGenerator()`) any place the engine asks for an
/// `inout some RandomNumberGenerator`.
public struct SeededRandomNumberGenerator: RandomNumberGenerator, Codable, Sendable, Hashable {
    public var state: UInt64

    public init(seed: UInt64) {
        // 0 is a fixed point of xorshift; substitute a non-zero constant.
        self.state = seed == 0 ? 0xDEAD_BEEF_CAFE_BABE : seed
    }

    /// Restore an RNG from a previously-captured `state`.
    public init(rawState: UInt64) { self.state = rawState }

    public mutating func next() -> UInt64 {
        state ^= state >> 12
        state ^= state << 25
        state ^= state >> 27
        return state &* 0x2545_F491_4F6C_DD1D
    }
}
