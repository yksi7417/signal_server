import { processAiTurns } from './aiTurnHandler.js';
import { showCelebrationScreen } from './celebrationScreen.js';
import { enableHumanTurn, hideClaimPrompt, showClaimPrompt } from './claimsHandler.js';
import { elements, store, clearAllTimeouts } from './gameStore.js';
import { displayDiscardedTiles, displayGameInfo, displayHand, displayRevealedSets } from './tileDisplay.js';

function autoSelectDrawnTile(drawnTile) {
    console.log("Auto-selecting drawn tile:", drawnTile);
    
    // Set the drawn tile as selected
    store.selectedTileForDiscard = drawnTile;
    
    // Update the selected tile display
    if (elements.selectedTileDisplayEl) {
        elements.selectedTileDisplayEl.textContent = `Selected: ${drawnTile}`;
    }
    
    // Find the tile element in the DOM and highlight it
    const tileElements = document.querySelectorAll('#player-hand span');
    tileElements.forEach(el => {
        // Reset all tile backgrounds first
        el.style.backgroundColor = 'transparent';
        
        // Find and highlight the drawn tile (last occurrence of this tile type)
        const tileText = el.textContent;
        if (tileText === drawnTile) {
            // Check if this is the last instance by checking if there are more of the same tile after this one
            const remainingElements = Array.from(tileElements).slice(Array.from(tileElements).indexOf(el) + 1);
            const hasMoreOfSameTile = remainingElements.some(remainingEl => remainingEl.textContent === tileText);
            
            // If this is the last occurrence of this tile type, it's likely the drawn tile
            if (!hasMoreOfSameTile) {
                el.style.backgroundColor = 'lightblue';
            }
        }
    });
      // Update console message to indicate auto-selection
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = `Drew: ${drawnTile}`;
    }
}

// Start the discard countdown timer with visual feedback
export function startDiscardCountdown(drawnTile) {
    let timeLeft = store.DISCARD_TIMEOUT_MS / 1000; // Convert to seconds
    
    // Clear any existing countdown
    if (store.discardCountdownId) {
        clearInterval(store.discardCountdownId);
        store.discardCountdownId = null;
    }
      // Update console with initial countdown
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = `Drew: ${drawnTile}. Auto-selected for discard. Auto-discard in ${timeLeft}s or press 'D'.`;
    }
      // Start countdown interval
    store.discardCountdownId = setInterval(() => {
        timeLeft--;
        const selectedTile = store.selectedTileForDiscard || drawnTile;
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = `Selected: ${selectedTile}. Auto-discard in ${timeLeft}s or press 'D'.`;
        }
        
        if (timeLeft <= 0) {
            clearInterval(store.discardCountdownId);
            store.discardCountdownId = null;
        }
    }, 1000);
      // Set the actual auto-discard timeout
    store.discardTimeoutId = setTimeout(async () => {
        // Clear countdown interval
        if (store.discardCountdownId) {
            clearInterval(store.discardCountdownId);
            store.discardCountdownId = null;
        }
        
        console.log(`Auto-discarding after ${store.DISCARD_TIMEOUT_MS / 1000} seconds`);
        
        // Check if no tile is selected, then auto-select the rightmost tile
        if (!store.selectedTileForDiscard && store.currentHandTiles.length > 0) {
            const rightmostTile = store.currentHandTiles[store.currentHandTiles.length - 1];
            store.selectedTileForDiscard = rightmostTile;
            
            // Update the selected tile display
            if (elements.selectedTileDisplayEl) {
                elements.selectedTileDisplayEl.textContent = `Selected: ${rightmostTile}`;
            }
            
            // Highlight the rightmost tile in the UI
            const tileElements = document.querySelectorAll('#player-hand span');
            tileElements.forEach((el, index) => {
                el.style.backgroundColor = 'transparent';
                if (index === tileElements.length - 1) {
                    el.style.backgroundColor = 'lightblue';
                }
            });
            
            if (elements.playerConsoleEl) {
                elements.playerConsoleEl.textContent = `Auto-selected and discarded: ${rightmostTile}`;
            }
        } else if (store.selectedTileForDiscard) {
            if (elements.playerConsoleEl) {
                elements.playerConsoleEl.textContent = `Auto-discarded: ${store.selectedTileForDiscard}`;
            }
        }
        
        // Trigger discard if tile is selected and discard button is enabled
        if (store.selectedTileForDiscard && elements.btnDiscardTile && !elements.btnDiscardTile.disabled) {
            await handleDiscardTile();
        }
    }, store.DISCARD_TIMEOUT_MS);
}

export async function handleDrawTile() {
    if (elements.playerConsoleEl) elements.playerConsoleEl.textContent = "";
    if (store.currentGameInfo.winner_found) {
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent =
                `Game over. Player ${store.currentGameInfo.winning_player_id} has won. Please reset.`;
        }
        return;
    }

    try {
        const response = await fetch('/api/draw_tile', { method: 'POST' });
        const result = await response.json();
        handleDrawTileResult(result);
    } catch (error) {
        console.error("Error calling draw_tile API:", error);
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = "Exception drawing tile: " + error;
        }
    }
}

export async function handleDiscardTile(pointerEvent) {
    try {
        // Clear any active discard timeout and countdown when manually discarding
        if (store.discardTimeoutId) {
            clearTimeout(store.discardTimeoutId);
            store.discardTimeoutId = null;
        }
        if (store.discardCountdownId) {
            clearInterval(store.discardCountdownId);
            store.discardCountdownId = null;
        }
        
        if (store.selectedTileForDiscard === null)
            throw new Error("No tile selected for discard.");

        const tile = store.selectedTileForDiscard
        const response = await fetch('/api/discard_tile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tile_to_discard: tile })
        });
        const result = await response.json();
        console.log("Discard result:", result);

        if (result && result.success) {
            displayHand(result.updated_hand);
            handleDiscardTileResult(result);
        }
    } catch (error) {
        console.error('Error handling tile discard:', error);
    }
}

async function loadInitialGameState() {
    console.log("Requesting new game state from Python...");
    
    // Clear any active timeouts when starting a new game
    clearAllTimeouts();
    
    try {
        const response = await fetch('/api/start_new_game', { method: 'POST' });
        const game_info_data = await response.json();
        if (game_info_data) {
            console.log("Received game state:", game_info_data);
            store.currentGameInfo = game_info_data; // This includes winner_found: false
            displayHand(store.currentGameInfo.player_hand);
            displayGameInfo(store.currentGameInfo);
            displayRevealedSets([]);
            hideClaimPrompt();

            if (store.currentGameInfo.winner_found) { // Should be false from start_new_game
                if (elements.playerConsoleEl) elements.playerConsoleEl.textContent = `Game over. Player ${store.currentGameInfo.winning_player_id} has won. Please reset.`;
                if (gameInfoEl && store.currentGameInfo.winning_player_id !== undefined) gameInfoEl.innerHTML += `<br><b>Player ${store.currentGameInfo.winning_player_id} WINS!</b>`;
                if (btnDrawTile) btnDrawTile.disabled = true;
                if (btnDiscardTile) btnDiscardTile.disabled = true;            } else if (store.currentGameInfo.current_player_id !== 0) {
                processAiTurns();            } else { // Player 0's turn and no winner
                if (elements.playerConsoleEl) elements.playerConsoleEl.textContent = "Game loaded. Auto-drawing tile...";
                // Auto-draw instead of waiting for manual draw
                setTimeout(async () => {
                    console.log("Starting auto-draw for player turn...");
                    await handleDrawTile();
                }, 100); // Small delay to ensure UI is ready
            }
        } else {
            console.error("Did not receive game info from backend.");
            if (playerHandEl) playerHandEl.textContent = "Error loading game.";
            if (elements.playerConsoleEl) elements.playerConsoleEl.textContent = "Error loading game from backend.";
        }
    } catch (error) {
        console.error("Error starting new game:", error);
        if (playerHandEl) playerHandEl.textContent = "Error connecting to backend.";
        if (elements.playerConsoleEl) elements.playerConsoleEl.textContent = "Error connecting to backend to start game.";
    }
}


function handleSuccessfulDraw(result) {
    // Check for self-draw win claim first
    if (result.human_can_claim === "SELF_DRAW_WIN") {
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = `Drew: ${result.drawn_tile} - You can WIN! Claim it?`;
        }
        showClaimPrompt(result.claimable_tile, "SELF_DRAW_WIN");
        return;
    }
      // Clear any existing discard timeout
    if (store.discardTimeoutId) {
        clearTimeout(store.discardTimeoutId);
        store.discardTimeoutId = null;
    }
    
    if (elements.btnDrawTile)
        elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile)
        elements.btnDiscardTile.disabled = false;
      // Auto-select the drawn tile
    if (result.drawn_tile) {
        autoSelectDrawnTile(result.drawn_tile);
        
        // Start countdown timer for auto-discard
        startDiscardCountdown(result.drawn_tile);
    }
}


function handleWinAfterDraw(result) {
    // Clear any active timeouts when game ends
    clearAllTimeouts();
    
    store.currentGameInfo.winner_found = true;
    store.currentGameInfo.winning_player_id = result.winning_player_id;

    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = `Player ${result.winning_player_id} WINS!`;
    }

    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;

    displayRevealedSets(result.revealed_sets);
    displayHand(result.hand);
    showCelebrationScreen(result.winning_player_id);
}

function handleWinAfterDiscard() {
    clearAllTimeouts();
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent =
            `Player ${store.currentGameInfo.winning_player_id} WINS!`;
    }
    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
    showCelebrationScreen(store.currentGameInfo.winning_player_id);
}

function handleWallEmpty(result) {
    store.currentGameInfo.winner_found = false;
    store.currentGameInfo.game_ended = true;

    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message || "Wall empty - game ends in a draw!";
    }

    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;

    displayHand(result.hand);
}

function handleDrawTileResult(result) {
    if (result && result.success) {
        updateGameStateAfterDraw(result);

        if (result.action === "win" && result.winner_found) {
            handleWinAfterDraw(result);
        } else if (result.action === "wall_empty") {
            handleWallEmpty(result);
        } else if (!result.winner_found) {
            handleSuccessfulDraw(result);
        }
    } else {
        handleDrawError(result);
    }
}

function updateGameInfoDisplay(result) {
    if (elements.gameInfoEl &&
        result.next_player_id !== undefined &&
        result.discarded_tile) {
        elements.gameInfoEl.innerHTML = `Wind: ${store.currentGameInfo.game_wind || 'N/A'}<br>`;
    }
}

function handleDrawError(result) {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent =
            result && result.message ? result.message : "Error drawing tile.";
    }
}

export function handleDiscardTileResult(result) {
    if (result && result.success) {
        updateGameStateAfterDiscard(result);
        if (result.human_can_claim && !store.currentGameInfo.winner_found) {
            showClaimPrompt(result.claimable_tile, result.human_can_claim);
        } else if (store.currentGameInfo.winner_found) {
            handleWinAfterDiscard();
        } else if (result.next_player_id !== 0) {
            updateGameInfoDisplay(result);
            if (result.discarded_by_player_id === 0)
                processAiTurns();
        } else {
            enableHumanTurn();
        }
    } else {
        handleDiscardError(result);
    }
}

function updateGameStateAfterDraw(result) {
    store.currentGameInfo.winner_found = result.winner_found;
    store.currentGameInfo.winning_player_id = result.winning_player_id;
    store.currentGameInfo.remaining_tiles = result.remaining_tiles;
    displayHand(result.hand);
    displayGameInfo(store.currentGameInfo);
}

export function updateGameStateAfterDiscard(result) {
    displayHand(result.updated_hand);
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent =
            `Discarded ${result.discarded_tile}.`;
    }
    store.selectedTileForDiscard = null;
    if (elements.selectedTileDisplayEl) {
        elements.selectedTileDisplayEl.textContent = "Selected:";
    }

    store.currentGameInfo.current_player_id = result.next_player_id;
    store.currentGameInfo.winner_found = result.winner_found;
    store.currentGameInfo.remaining_tiles = result.remaining_tiles;

    store.discardedTiles.push(result.discarded_tile);
    displayDiscardedTiles();
}

export async function handleReset() {
    // Clear all active timeouts when resetting
    clearAllTimeouts();
    
    await fetch('/api/reset_game', { method: 'POST' });
    console.log("Game reset on backend. Reloading initial state...");
    loadInitialGameState();
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = "Game reset. New game started.";
    }
    if (elements.selectedTileDisplayEl) {
        elements.selectedTileDisplayEl.textContent = "Selected:";
    }
    store.discardedTiles = [];
    displayDiscardedTiles();

    store.selectedTileForDiscard = null;
    displayRevealedSets([]);
    hideClaimPrompt();
    if (store.currentGameInfo) {
        store.currentGameInfo.winner_found = false;
    }
    // The loadInitialGameState() function will handle auto-drawing when appropriate
}
