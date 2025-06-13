// Game state store and DOM element references
export const store = {
    currentGameInfo: {
        game_wind: null,
        current_player_id: null,
        winner_found: false,
        winning_player_id: null,
        remaining_tiles: null
    },
    selectedTileForDiscard: null,
    currentHandTiles: [],
    discardedTiles: [],
    INIT_HAND_SIZE: 13,
    claimType: null,
    claimableTile: null,
    activeClaimType: null, // Will track the type of claim being made (PUNG, KONG, WIN)    // Timeout management
    claimTimeoutId: null,
    discardTimeoutId: null,
    discardCountdownId: null, // For visual countdown display
    CLAIM_TIMEOUT_MS: 5000, // 5 seconds for claim decisions
    DISCARD_TIMEOUT_MS: 5000 // 5 seconds for discard actions
};

// DOM element references
export const elements = {
    btnReset: document.getElementById('reset'),
    gameInfoEl: document.getElementById('game-info'),
    playerHandEl: document.getElementById('player-hand'),
    btnDrawTile: document.getElementById('btnDrawTile'),
    btnDiscardTile: document.getElementById('btnDiscardTile'),
    playerConsoleEl: document.getElementById('player-console'),
    selectedTileDisplayEl: document.getElementById('selected-tile-display'),
    btnClaimYes: document.getElementById('btnClaimYes'),
    btnClaimNo: document.getElementById('btnClaimNo'),
    revealedSetsEl: document.getElementById('revealed-sets-display'),
    discardArea: document.getElementById('discard-area')
};

// Utility function to clear all active timeouts
export function clearAllTimeouts() {
    if (store.claimTimeoutId) {
        clearTimeout(store.claimTimeoutId);
        store.claimTimeoutId = null;
    }
    if (store.discardTimeoutId) {
        clearTimeout(store.discardTimeoutId);
        store.discardTimeoutId = null;
    }
    if (store.discardCountdownId) {
        clearInterval(store.discardCountdownId);
        store.discardCountdownId = null;
    }
}
