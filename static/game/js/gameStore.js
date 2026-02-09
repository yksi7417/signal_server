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
    selectedTileIndex: -1,
    currentHandTiles: [],
    discardedTiles: [],
    playersInfo: [],
    INIT_HAND_SIZE: 13,
    claimType: null,
    claimableTile: null,
    activeClaimType: null, // Will track the type of claim being made (PUNG, KONG, WIN)    // Timeout management
    claimTimeoutId: null,
    claimCountdownId: null, // For visual countdown display
    claimCountdownSeconds: 0, // Current countdown value
    discardTimeoutId: null,
    discardCountdownId: null, // For visual countdown display
    CLAIM_TIMEOUT_MS: 30000, // 30 seconds for claim decisions (configurable for debugging)
    DISCARD_TIMEOUT_MS: 30000 // 30 seconds for discard actions (configurable via slider)
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
    // Per-player element refs for 4-player table
    playerAreas: [0,1,2,3].map(i => document.getElementById(`player-area-${i}`)),
    playerLabels: [0,1,2,3].map(i => document.getElementById(`player-label-${i}`)),
    playerMelds: [0,1,2,3].map(i => document.getElementById(`player-melds-${i}`)),
    playerDiscards: [0,1,2,3].map(i => document.getElementById(`player-discards-${i}`)),
    playerHandCounts: [0,1,2,3].map(i => document.getElementById(`player-hand-count-${i}`)),
};

// Utility function to clear all active timeouts
export function clearAllTimeouts() {
    if (store.claimTimeoutId) {
        clearTimeout(store.claimTimeoutId);
        store.claimTimeoutId = null;
    }
    if (store.claimCountdownId) {
        clearInterval(store.claimCountdownId);
        store.claimCountdownId = null;
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
