import { processAiTurns } from './aiTurnHandler.js';
import { showCelebrationScreen } from './celebrationScreen.js';
import { apiUrl } from './config.js';
import { startDiscardCountdown } from './gameActions.js';
import { elements, store, clearAllTimeouts } from './gameStore.js';
import { displayHand, displayPlayersInfo, displayRevealedSets, selectTileByIndex } from './tileDisplay.js';

export function showClaimPrompt(tile, claimType) {
    store.activeClaimType = claimType;

    // Clear any existing claim timeout and countdown
    if (store.claimTimeoutId) {
        clearTimeout(store.claimTimeoutId);
        store.claimTimeoutId = null;
    }
    if (store.claimCountdownId) {
        clearInterval(store.claimCountdownId);
        store.claimCountdownId = null;
    }

    // Initialize countdown
    store.claimCountdownSeconds = Math.floor(store.CLAIM_TIMEOUT_MS / 1000);

    if (claimType === "SELF_DRAW_WIN") {
        // Update initial message
        elements.playerConsoleEl.textContent =
            `You drew ${tile} and can WIN! Do you want to claim WIN? (${store.claimCountdownSeconds}s)`;

        // Start countdown display (but no auto-decline for self-draw wins)
        store.claimCountdownId = setInterval(() => {
            store.claimCountdownSeconds--;
            if (store.claimCountdownSeconds > 0 && elements.playerConsoleEl) {
                elements.playerConsoleEl.textContent =
                    `You drew ${tile} and can WIN! Do you want to claim WIN? (${store.claimCountdownSeconds}s)`;
            }
        }, 1000);
    } else {
        // Update initial message
        elements.playerConsoleEl.textContent =
            `Player discarded ${tile}. Do you want to claim ${claimType}? (Auto-decline in ${store.claimCountdownSeconds}s)`;

        // Start countdown display
        store.claimCountdownId = setInterval(() => {
            store.claimCountdownSeconds--;
            if (store.claimCountdownSeconds > 0 && elements.playerConsoleEl) {
                elements.playerConsoleEl.textContent =
                    `Player discarded ${tile}. Do you want to claim ${claimType}? (Auto-decline in ${store.claimCountdownSeconds}s)`;
            }
        }, 1000);

        // Set timeout to automatically decline claims
        store.claimTimeoutId = setTimeout(() => {
            console.log(`Auto-declining ${claimType} claim after ${store.CLAIM_TIMEOUT_MS / 1000} seconds`);
            if (elements.playerConsoleEl) {
                elements.playerConsoleEl.textContent = `Auto-declined ${claimType} claim due to timeout.`;
            }
            handleClaimNo();
        }, store.CLAIM_TIMEOUT_MS);
    }

    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
    if (elements.btnClaimNo) elements.btnClaimNo.disabled = false;
    if (elements.btnClaimYes) elements.btnClaimYes.disabled = false;
}

export function hideClaimPrompt() {
    // Clear any active claim timeout and countdown
    if (store.claimTimeoutId) {
        clearTimeout(store.claimTimeoutId);
        store.claimTimeoutId = null;
    }
    if (store.claimCountdownId) {
        clearInterval(store.claimCountdownId);
        store.claimCountdownId = null;
    }

    if (elements.btnClaimNo) elements.btnClaimNo.disabled = true;
    if (elements.btnClaimYes) elements.btnClaimYes.disabled = true;
}

export async function handleClaimYes() {
    // Clear any active claim timeout when manually responding
    if (store.claimTimeoutId) {
        clearTimeout(store.claimTimeoutId);
        store.claimTimeoutId = null;
    }

    if (store.activeClaimType === 'PUNG') {
        await handleClaimPungYes();
    } else if (store.activeClaimType === 'CHOW') {
        await handleClaimChowYes();
    } else if (store.activeClaimType === 'KONG') {
        await handleClaimKongYes();
    } else if (store.activeClaimType === 'WIN' || store.activeClaimType === 'SELF_DRAW_WIN') {
        await handleClaimWinYes();
    }
}

export async function handleClaimNo() {
    // Clear any active claim timeout when manually responding
    if (store.claimTimeoutId) {
        clearTimeout(store.claimTimeoutId);
        store.claimTimeoutId = null;
    }

    if (store.activeClaimType === 'PUNG') {
        await handleClaimPungNo();
    } else if (store.activeClaimType === 'CHOW') {
        await handleClaimChowNo();
    } else if (store.activeClaimType === 'KONG') {
        await handleClaimKongNo();
    } else if (store.activeClaimType === 'WIN' || store.activeClaimType === 'SELF_DRAW_WIN') {
        await handleClaimWinNo();
    }
}

export async function handleClaimPungYes() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch(apiUrl('/api/player_claims_pung'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: true })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (result && result.success) {
        handleSuccessfulClaim(result);
    } else {
        handleFailedPungClaim(result);
    }
}

export async function handleClaimPungNo() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch(apiUrl('/api/player_claims_pung'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: false })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message;
    }

    if (result && result.success && result.action === "claim_declined") {
        handleClaimDeclined(result);
    } else {
        if (result?.winner_found !== undefined) {
            store.currentGameInfo.winner_found = result.winner_found;
        }
    }
}

export async function handleClaimChowYes() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch(apiUrl('/api/player_claims_chow'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: true })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (result && result.success) {
        handleSuccessfulChowClaim(result);
    } else {
        handleFailedChowClaim(result);
    }
}

export async function handleClaimChowNo() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch(apiUrl('/api/player_claims_chow'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: false })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message;
    }

    if (result && result.success && result.action === "claim_declined") {
        handleClaimDeclined(result);
    } else {
        if (result?.winner_found !== undefined) {
            store.currentGameInfo.winner_found = result.winner_found;
        }
    }
}

export async function handleClaimKongYes() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch(apiUrl('/api/player_claims_kong'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: true })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (result && result.success) {
        handleSuccessfulKongClaim(result);
    } else {
        handleFailedKongClaim(result);
    }
}

export async function handleClaimKongNo() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch(apiUrl('/api/player_claims_kong'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: false })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (result && result.success && result.action === "claim_declined") {
        handleClaimDeclined(result);
    }
}

function handleSuccessfulClaim(result) {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message;
    }
    displayHand(result.player_hand);
    displayRevealedSets(result.revealed_sets);
    displayPlayersInfo(result.players_info, result.current_player_id);

    store.currentGameInfo.winner_found = result.winner_found;
    store.currentGameInfo.winning_player_id = result.winning_player_id;

    if (store.currentGameInfo.winner_found) {
        handleWinAfterClaim();
    } else if (result.action === "discard_after_pung") {
        enableDiscardAfterClaim();
    }
}

function handleFailedPungClaim(result) {
    if (elements.playerConsoleEl && result) {
        elements.playerConsoleEl.textContent = "Error claiming Pung: " + (result.message || "Unknown");
    }
    if (result?.winner_found !== undefined) {
        store.currentGameInfo.winner_found = result.winner_found;
    }
}

function handleSuccessfulChowClaim(result) {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message;
    }
    displayHand(result.player_hand);
    displayRevealedSets(result.revealed_sets);
    displayPlayersInfo(result.players_info, result.current_player_id);

    store.currentGameInfo.winner_found = result.winner_found;
    store.currentGameInfo.winning_player_id = result.winning_player_id;

    if (store.currentGameInfo.winner_found) {
        handleWinAfterClaim();
    } else if (result.action === "discard_after_chow") {
        enableDiscardAfterClaim();
    }
}

function handleFailedChowClaim(result) {
    if (elements.playerConsoleEl && result) {
        elements.playerConsoleEl.textContent = "Error claiming Chow: " + (result.message || "Unknown");
    }
    if (result?.winner_found !== undefined) {
        store.currentGameInfo.winner_found = result.winner_found;
    }
}

function handleClaimDeclined(result) {
    store.currentGameInfo.current_player_id = result.next_player_id;
    store.currentGameInfo.winner_found = result.winner_found;
    store.currentGameInfo.winning_player_id = result.winning_player_id;

    displayPlayersInfo(result.players_info, result.current_player_id);
    updateGameInfoAfterDecline(result);

    if (store.currentGameInfo.winner_found) {
        handleWinAfterClaimDecline();
    } else if (result.next_player_id !== 0) {
        processAiTurns();
    } else {
        enableHumanTurn();
    }
}

function handleWinAfterClaim() {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent =
            `Player ${store.currentGameInfo.winning_player_id} WINS! (After Pung claim processing path)`;
    }
    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
}

function handleWinAfterClaimDecline() {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent =
            `Player ${store.currentGameInfo.winning_player_id} WINS! (After claim decline processing path)`;
    }
    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
}

function enableDiscardAfterClaim() {
    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = false;

    // Auto-select leftmost tile and start discard countdown
    if (store.currentHandTiles && store.currentHandTiles.length > 0) {
        selectTileByIndex(0);
        startDiscardCountdown(store.currentHandTiles[0]);
    }
}

export function enableHumanTurn() {
    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;  // Disable manual draw
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
    
    // Auto-draw when it's the player's turn
    autoDrawTile();
}

async function autoDrawTile() {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = "Your turn - automatically drawing tile...";
    }
    
    console.log("Auto-drawing tile for player turn...");
    
    try {
        // Import and call the draw tile function
        const { handleDrawTile } = await import('./gameActions.js');
        await handleDrawTile();
    } catch (error) {
        console.error("Error during auto-draw:", error);
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = "Error auto-drawing tile. Try manually.";
        }
        // Fallback to manual mode
        if (elements.btnDrawTile) elements.btnDrawTile.disabled = false;
    }
}

function updateGameInfoAfterDecline(result) {
    if (elements.gameInfoEl && result.next_player_id !== undefined && result.discarded_tile) {
        elements.gameInfoEl.innerHTML = `
            Wind: ${store.currentGameInfo.game_wind || 'N/A'}<br> 
        `;
    }
}

async function handleClaimWinYes() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch(apiUrl('/api/player_claims_win'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: true })
    });
    const result = await response.json();
    hideClaimPrompt();    if (result && result.success) {
        // Clear timeouts when win is claimed
        if (result.action === "win_claimed") {
            clearAllTimeouts();
        }

        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = result.message;
        }
        displayPlayersInfo(result.players_info, result.current_player_id);
        store.currentGameInfo.winner_found = result.winner_found;
        store.currentGameInfo.winning_player_id = result.winning_player_id;
        if (result.winning_hand) store.currentGameInfo.winning_hand = result.winning_hand;
        if (result.winning_revealed_sets) store.currentGameInfo.winning_revealed_sets = result.winning_revealed_sets;

        if (result.action === "win_claimed") {
            showCelebrationScreen(result.winning_player_id);
        }

        if (result.hand) {
            displayHand(result.hand);
        }
        if (result.revealed_sets) {
            displayRevealedSets(result.revealed_sets);
        }
    } else {
        handleFailedClaim(result);
    }
}

async function handleClaimWinNo() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch(apiUrl('/api/player_claims_win'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: false })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message;
    }

    // Handle different types of claim declines
    if (result && result.success) {        if (result.action === "self_draw_win_declined") {
            // For self-draw win declines, enable discarding
            if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = false;
            
            // Auto-select the last tile (drawn tile) for easy discarding
            if (store.currentHandTiles && store.currentHandTiles.length > 0) {
                const lastTile = store.currentHandTiles[store.currentHandTiles.length - 1];
                store.selectedTileForDiscard = lastTile;
                
                // Update the selected tile display
                if (elements.selectedTileDisplayEl) {
                    elements.selectedTileDisplayEl.textContent = `Selected: ${lastTile}`;
                }
                
                // Highlight the last tile in the UI
                const tileElements = document.querySelectorAll('#player-hand span');
                tileElements.forEach((el, index) => {
                    el.classList.remove('tile-selected');
                    if (index === tileElements.length - 1) {
                        el.classList.add('tile-selected');
                    }
                });
            }
        } else if (result.action === "claim_declined") {
            handleClaimDeclined(result);
        }
    }
}

function handleSuccessfulWinClaim(result) {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message || `Player ${result.winning_player_id} WINS!`;
    }
    if (result.hand) displayHand(result.hand);
    if (result.revealed_sets) displayRevealedSets(result.revealed_sets);

    store.currentGameInfo.winner_found = result.winner_found;
    store.currentGameInfo.winning_player_id = result.winning_player_id;

    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
}

function handleFailedWinClaim(result) {
    if (elements.playerConsoleEl && result) {
        elements.playerConsoleEl.textContent = "Error claiming Win: " + (result.message || "Unknown error");
    }
    if (result?.winner_found !== undefined) {
        store.currentGameInfo.winner_found = result.winner_found;
    }
}

function handleSuccessfulKongClaim(result) {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message;
    }
    displayHand(result.hand);
    displayRevealedSets(result.revealed_sets);
    displayPlayersInfo(result.players_info, result.current_player_id);

    store.currentGameInfo.winner_found = result.winner_found;
    store.currentGameInfo.winning_player_id = result.winning_player_id;

    if (store.currentGameInfo.winner_found) {
        handleWinAfterClaim();
    } else {
        enableDiscardAfterClaim();
    }
}

function handleFailedKongClaim(result) {
    if (elements.playerConsoleEl && result) {
        elements.playerConsoleEl.textContent = "Error claiming Kong: " + (result.message || "Unknown");
    }
    if (result?.winner_found !== undefined) {
        store.currentGameInfo.winner_found = result.winner_found;
    }
}

