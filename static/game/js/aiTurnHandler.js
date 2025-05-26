import { store, elements } from './gameStore.js';
import { displayHand, displayRevealedSets, displayGameInfo, displayDiscardedTiles } from './tileDisplay.js';
import { hideClaimPrompt, showClaimPrompt } from './claimsHandler.js';

export async function processAiTurns() {
    if (!store.currentGameInfo || store.currentGameInfo.current_player_id === undefined) {
        console.log("Waiting for game state...");
        return;
    }
    
    if (store.currentGameInfo.winner_found) {
        handleGameOver();
        return;
    }

    try {
        let next_player_is_ai = store.currentGameInfo.current_player_id !== 0;

        while (next_player_is_ai && !store.currentGameInfo.winner_found) {
            try {
                next_player_is_ai = await processSingleAiTurn();
                
                if (next_player_is_ai && !store.currentGameInfo.winner_found) {
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            } catch (error) {
                console.error("Error during AI turn processing:", error);
                break;
            }
        }

        if (store.currentGameInfo.winner_found) {
            handleGameOver();
        }
    } catch (error) {
        console.error("Error in AI turn processing:", error);
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = "Error during AI turn. Please reset the game.";
        }
    }
}

function handleGameOver() {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = 
            `Game over. Player ${store.currentGameInfo.winning_player_id} has won. Please reset.`;
    }
    if (elements.gameInfoEl && store.currentGameInfo.winning_player_id !== undefined) {
        elements.gameInfoEl.innerHTML += `<br><b>Player ${store.currentGameInfo.winning_player_id} WINS!</b>`;
    }
    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
}

async function processSingleAiTurn() {
    updateUIForAiTurn();

    try {
        const ai_turn_result = await eel.eel_request_ai_turn()();
        if (!ai_turn_result) {
            throw new Error("No result from AI turn");
        }

        // Update discarded tiles if present in the AI turn result
        if (ai_turn_result.discardedTile) {
            store.discardedTiles.push(ai_turn_result.discardedTile);
            displayDiscardedTiles();
        }

        updateGameState(ai_turn_result);
        
        if (ai_turn_result.success) {
            return handleSuccessfulAiTurn(ai_turn_result);
        } else {
            handleFailedAiTurn(ai_turn_result);
            return false;
        }
    } catch (error) {
        console.error("Error during AI turn processing:", error);
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = "Error during AI turn. Try resetting the game.";
        }
        return false;
    }
}

function updateUIForAiTurn() {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = 
            `Player ${store.currentGameInfo.current_player_id} (AI) is thinking...`;
    }
    
    if(elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if(elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
    hideClaimPrompt();
}

function updateGameState(result) {
    if (!result) return;
    
    if (result.winner_found !== undefined) {
        store.currentGameInfo.winner_found = result.winner_found;
    }
    if (result.winning_player_id !== undefined) {
        store.currentGameInfo.winning_player_id = result.winning_player_id;
    }
}

function handleSuccessfulAiTurn(result) {
    if (!result) return false;

    if (result.player0_hand) displayHand(result.player0_hand);
    if (result.player0_revealed_sets) displayRevealedSets(result.player0_revealed_sets);

    if (result.action === "win" && result.winner_found) {
        handleGameOver();
        return true;
    }
    
    if (result.discarded_tile) {
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = 
                `AI Player ${result.ai_player_id} discarded ${result.discarded_tile.unicode}`;
        }
    }
    
    return result.next_player_id !== 0;
}

function handleFailedAiTurn(result) {
    if (elements.playerConsoleEl && result && result.error) {
        elements.playerConsoleEl.textContent = "AI turn issue: " + result.error;
    } else if (elements.playerConsoleEl && !store.currentGameInfo.winner_found) {
        elements.playerConsoleEl.textContent = "Waiting for your action.";
    }

    if(result?.player0_hand) displayHand(result.player0_hand);
    if(result?.player0_revealed_sets) displayRevealedSets(result.player0_revealed_sets);

    handleGameStateAfterFailedTurn(result);
}

function handleGameStateAfterFailedTurn(result) {
    if(store.currentGameInfo.winner_found) {
        handleGameOver();
    } else if(result?.human_can_claim_pung) {
        showClaimPrompt(result.claimable_tile, "PUNG");
    } else if (!store.currentGameInfo.winner_found) {
        if(elements.btnDrawTile) elements.btnDrawTile.disabled = false;
        if(elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
    }
}
