// Game state store and DOM element references
export const store = {
    currentGameInfo: {
        game_wind: null,
        current_player_id: null,
        winner_found: false,
        winning_player_id: null
    },
    selectedTileForDiscard: null,
    currentHandTiles: [],
    discardedTiles: [],
    INIT_HAND_SIZE: 13,
    claimType: null,
    claimableTile: null
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
    claimPromptEl: document.getElementById('claim-prompt'),
    claimMessageEl: document.getElementById('claim-message'),
    btnClaimYes: document.getElementById('btnClaimYes'),
    btnClaimNo: document.getElementById('btnClaimNo'),
    revealedSetsEl: document.getElementById('revealed-sets-display'),
    discardArea: document.getElementById('discard-area'),
    claimTypeEl: document.getElementById('claim-type')
};
