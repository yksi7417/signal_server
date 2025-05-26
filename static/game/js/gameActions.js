import { store, elements } from './gameStore.js';
import { displayHand, displayRevealedSets, displayGameInfo } from './tileDisplay.js';
import { processAiTurns } from './aiTurnHandler.js';
import { showClaimPrompt, hideClaimPrompt } from './claimsHandler.js';

export async function handleDrawTile() {
    if(elements.playerConsoleEl) elements.playerConsoleEl.textContent = "";
    if (store.currentGameInfo.winner_found) {
        if(elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = 
                `Game over. Player ${store.currentGameInfo.winning_player_id} has won. Please reset.`;
        }
        return;
    }

    try {
        const result = await eel.eel_draw_tile()();
        handleDrawTileResult(result);
    } catch (error) {
        console.error("Error calling eel_draw_tile:", error);
        if(elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = "Exception drawing tile: " + error;
        }
    }
}

export async function handleDiscardTile() {
    if (store.currentGameInfo.winner_found) {
        if(elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = 
                `Game over. Player ${store.currentGameInfo.winning_player_id} has won. Please reset.`;
        }
        return;
    }

    if (!store.selectedTileForDiscard) {
        if(elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = "Please select a tile from your hand to discard.";
        }
        return;
    }

    try {
        const result = await eel.eel_discard_tile(store.selectedTileForDiscard)();
        handleDiscardTileResult(result);
    } catch (error) {
        console.error("Error calling eel_discard_tile:", error);
        if(elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = "Exception discarding tile: " + error;
        }
    }
}

function handleDrawTileResult(result) {
    if (result && result.success) {
        updateGameStateAfterDraw(result);
        
        if (result.action === "win" && result.winner_found) {
            handleWinAfterDraw(result);
        } else if (!result.winner_found) {
            handleSuccessfulDraw(result);
        }
    } else {
        handleDrawError(result);
    }
}

function handleDiscardTileResult(result) {
    if (result && result.success) {
        updateGameStateAfterDiscard(result);
        
        if (result.human_can_claim_pung && !store.currentGameInfo.winner_found) {
            showClaimPrompt(result.claimable_tile, "PUNG");
        } else if (store.currentGameInfo.winner_found) {
            handleWinAfterDiscard();
        } else if (result.next_player_id !== 0) {
            updateGameInfoDisplay(result);
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
    displayHand(result.hand);
}

function updateGameStateAfterDiscard(result) {
    displayHand(result.updated_hand);
    if(elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = 
            `Discarded ${store.selectedTileForDiscard.suit} ${store.selectedTileForDiscard.value}.`;
    }
    store.selectedTileForDiscard = null;
    if(elements.selectedTileDisplayEl) {
        elements.selectedTileDisplayEl.textContent = "Selected Tile: None";
    }
    
    store.currentGameInfo.current_player_id = result.next_player_id;
    store.currentGameInfo.winner_found = result.winner_found;
}

export async function handleReset() {
    await eel.reset_game()();
    console.log("Game reset on backend. Reloading initial state...");
    loadInitialGameState();
    if(elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = "Game reset. New game started.";
    }
    if(elements.selectedTileDisplayEl) {
        elements.selectedTileDisplayEl.textContent = "Selected Tile: None";
    }
    store.selectedTileForDiscard = null;
    displayRevealedSets([]);
    hideClaimPrompt();
    if(store.currentGameInfo) {
        store.currentGameInfo.winner_found = false;
    }
    if(elements.btnDrawTile) elements.btnDrawTile.disabled = false;
    if(elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
}
