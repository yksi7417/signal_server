import { processAiTurns } from './aiTurnHandler.js';
import { enableHumanTurn, hideClaimPrompt, showClaimPrompt } from './claimsHandler.js';
import { elements, store } from './gameStore.js';
import { displayDiscardedTiles, displayGameInfo, displayHand, displayRevealedSets } from './tileDisplay.js';

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
    if (elements.playerConsoleEl)
        elements.playerConsoleEl.textContent = `Drew: ${result.drawn_tile.suit} ${result.drawn_tile.value}. You now have 14 tiles. Select one to discard.`;
    if (elements.btnDrawTile)
        elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile)
        elements.btnDiscardTile.disabled = false;
}


function handleWinAfterDraw(result) {
    store.currentGameInfo.winner_found = true;
    store.currentGameInfo.winning_player_id = result.winning_player_id;

    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = `Player ${result.winning_player_id} WINS!`;
    }

    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;

    displayRevealedSets(result.revealed_sets);
    displayHand(result.hand);
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
            `Discarded ${result.discarded_tile.suit} ${result.discarded_tile.value}.`;
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
