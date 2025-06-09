import { hideClaimPrompt, showClaimPrompt } from './claimsHandler.js';
import { handleDiscardTileResult } from './gameActions.js';
import { elements, store } from './gameStore.js';
import { displayGameInfo, displayHand, displayRevealedSets } from './tileDisplay.js';

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

        while (next_player_is_ai && !store.currentGameInfo.winner_found && !store.currentGameInfo.game_ended) {
            try {
                next_player_is_ai = await processSingleAiTurn();
                if (next_player_is_ai && !store.currentGameInfo.winner_found && !store.currentGameInfo.game_ended) {
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            } catch (error) {
                console.error("Error during AI turn processing:", error);
                break;
            }
        }

        if (store.currentGameInfo.winner_found || store.currentGameInfo.game_ended) {
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
    if (store.currentGameInfo.winner_found) {
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent =
                `Game over. Player ${store.currentGameInfo.winning_player_id} has won. Please reset.`;
        }
        if (elements.gameInfoEl && store.currentGameInfo.winning_player_id !== undefined) {
            elements.gameInfoEl.innerHTML += `<br><b>Player ${store.currentGameInfo.winning_player_id} WINS!</b>`;
        }
    } else if (store.currentGameInfo.game_ended) {
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = "Draw game - Wall empty. Click 'Start New Hand' to continue.";
        }
        if (elements.gameInfoEl) {
            elements.gameInfoEl.innerHTML += `<br><b>DRAW GAME - Wall Empty!</b>`;
        }
        
        // For draw games, offer to start a new hand
        addStartNewHandButton();
    }
    
    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
}

function addStartNewHandButton() {
    // Check if button already exists
    if (document.getElementById('btnStartNewHand')) {
        return;
    }
    
    const newHandButton = document.createElement('button');
    newHandButton.id = 'btnStartNewHand';
    newHandButton.textContent = 'Start New Hand';
    newHandButton.className = 'btn btn-primary';
    newHandButton.style.marginLeft = '10px';
    
    newHandButton.onclick = async () => {
        try {
            // Advance dealer rotation (dealer stays same for draw games in some variants)
            const advanceResponse = await fetch('/api/advance_dealer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dealer_won: false }) // Draw = dealer didn't win
            });
            
            if (advanceResponse.ok) {
                // Start new game
                const newGameResponse = await fetch('/api/start_new_game', { method: 'POST' });
                const gameData = await newGameResponse.json();
                
                // Update the UI with new game data
                window.location.reload(); // Simple approach - reload the page
            }
        } catch (error) {
            console.error('Error starting new hand:', error);
            if (elements.playerConsoleEl) {
                elements.playerConsoleEl.textContent = 'Error starting new hand. Please refresh the page.';
            }
        }
    };
    
    // Add the button to the UI
    if (elements.btnDrawTile && elements.btnDrawTile.parentNode) {
        elements.btnDrawTile.parentNode.appendChild(newHandButton);
    }
}

async function processSingleAiTurn() {
    updateUIForAiTurn();

    try {
        const response = await fetch('/api/request_ai_turn', { method: 'POST' });
        const ai_turn_result = await response.json();
        if (!ai_turn_result) {
            throw new Error("No result from AI turn");
        }
        console.log("AI turn result:", ai_turn_result);
        handleDiscardTileResult(ai_turn_result);
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

    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
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
    if (result.remaining_tiles !== undefined) {
        store.currentGameInfo.remaining_tiles = result.remaining_tiles;
    }
    if (result.next_player_id !== undefined) {
        store.currentGameInfo.current_player_id = result.next_player_id;
    }
    if (result.game_ended !== undefined) {
        store.currentGameInfo.game_ended = result.game_ended;
    }
    
    // Update the game info display to reflect changes
    displayGameInfo(store.currentGameInfo);
}

function handleSuccessfulAiTurn(result) {
    if (!result) return false;

    if (result.player0_hand) displayHand(result.player0_hand);
    if (result.player0_revealed_sets) displayRevealedSets(result.player0_revealed_sets);

    if (result.action === "win" && result.winner_found) {
        handleGameOver();
        return true;
    }

    if (result.action === "wall_empty") {
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = result.message || "Wall empty - game ends in a draw!";
        }
        if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
        if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
        store.currentGameInfo.game_ended = true;
        return true; // Stop AI turns
    }

    if (result.discarded_tile) {
        if (elements.playerConsoleEl) {
            let displayText = `AI Player ${result.ai_player_id} discarded ${result.discarded_tile.unicode}`;
            if (result.human_can_claim) {
                displayText += `\n and you can claim it as a ${result.human_can_claim}.`;
                showClaimPrompt(result.discarded_tile, result.human_can_claim);
            }
            elements.playerConsoleEl.textContent = displayText
        }
    }

    return result.next_player_id !== 0 && !result.human_can_claim;
}

function handleFailedAiTurn(result) {
    // Check if this is actually a wall empty condition that erroneously returned success: false
    if (result && result.error && result.error.includes("Wall empty")) {
        // Treat this as a successful wall empty condition
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = "Wall empty - game ends in a draw!";
        }
        if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
        if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
        store.currentGameInfo.game_ended = true;
        handleGameOver();
        return;
    }
    
    if (elements.playerConsoleEl && result && result.error) {
        elements.playerConsoleEl.textContent = "AI turn issue: " + result.error;
    } else if (elements.playerConsoleEl && !store.currentGameInfo.winner_found) {
        elements.playerConsoleEl.textContent = "Waiting for your action.";
    }

    if (result?.player0_hand) displayHand(result.player0_hand);
    if (result?.player0_revealed_sets) displayRevealedSets(result.player0_revealed_sets);

    handleGameStateAfterFailedTurn(result);
}

function handleGameStateAfterFailedTurn(result) {
    if (store.currentGameInfo.winner_found) {
        handleGameOver();
    } else if (result?.human_can_claim) {
        showClaimPrompt(result.claimable_tile, result?.human_can_claim);
    } else if (!store.currentGameInfo.winner_found) {
        if (elements.btnDrawTile) elements.btnDrawTile.disabled = false;
        if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
    }
}
