import { store, elements } from './gameStore.js';
import { displayHand, displayRevealedSets, displayGameInfo, displayDiscardedTiles } from './tileDisplay.js';
import { processAiTurns } from './aiTurnHandler.js';
import { showClaimPrompt, hideClaimPrompt, enableHumanTurn } from './claimsHandler.js';

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

export async function handleDiscardTile(pointerEvent) {
    try {
        if (store.selectedTileForDiscard === null) 
            throw new Error("No tile selected for discard.");

        const tile = store.selectedTileForDiscard
        const result = await eel.eel_discard_tile(tile)();
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
    const game_info_data = await eel.start_new_game()(); 
    if (game_info_data) {
      console.log("Received game state:", game_info_data);
      store.currentGameInfo = game_info_data; // This includes winner_found: false
      displayHand(store.currentGameInfo.player_hand);
      displayGameInfo(store.currentGameInfo); 
      displayRevealedSets([]); 
      hideClaimPrompt(); 
      
      if (store.currentGameInfo.winner_found) { // Should be false from start_new_game
         if(elements.playerConsoleEl) elements.playerConsoleEl.textContent = `Game over. Player ${store.currentGameInfo.winning_player_id} has won. Please reset.`;
         if(gameInfoEl && store.currentGameInfo.winning_player_id !== undefined) gameInfoEl.innerHTML += `<br><b>Player ${store.currentGameInfo.winning_player_id} WINS!</b>`;
         if(btnDrawTile) btnDrawTile.disabled = true;
         if(btnDiscardTile) btnDiscardTile.disabled = true;
      } else if (store.currentGameInfo.current_player_id !== 0) { 
          processAiTurns();
      } else { // Player 0's turn and no winner
          if(btnDrawTile) btnDrawTile.disabled = false;
          if(btnDiscardTile) btnDiscardTile.disabled = true;
          if(elements.playerConsoleEl) elements.playerConsoleEl.textContent = "Game loaded. Your turn to draw.";
      }
    } else {
      console.error("Did not receive game info from backend.");
      if (playerHandEl) playerHandEl.textContent = "Error loading game.";
      if(elements.playerConsoleEl) elements.playerConsoleEl.textContent = "Error loading game from backend.";
    }
  } catch (error) {
    console.error("Error starting new game:", error);
    if (playerHandEl) playerHandEl.textContent = "Error connecting to backend.";
    if(elements.playerConsoleEl) elements.playerConsoleEl.textContent = "Error connecting to backend to start game.";
  }
}


function handleSuccessfulDraw(result) {
    if(elements.playerConsoleEl) 
        elements.playerConsoleEl.textContent = `Drew: ${result.drawn_tile.suit} ${result.drawn_tile.value}. You now have 14 tiles. Select one to discard.`;
    if(elements.btnDrawTile) 
        elements.btnDrawTile.disabled = true;
    if(elements.btnDiscardTile) 
        elements.btnDiscardTile.disabled = false;
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

function updateGameInfoDisplay(result) {
    if (elements.gameInfoEl && 
        result.next_player_id !== undefined && 
        result.discarded_tile) {
        elements.gameInfoEl.innerHTML = `Game Wind: ${store.currentGameInfo.game_wind || 'N/A'}<br>`;
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
    displayHand(result.hand);
}

export function updateGameStateAfterDiscard(result) {
    displayHand(result.updated_hand);
    if(elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = 
            `Discarded ${result.discarded_tile.suit} ${result.discarded_tile.value}.`;
    }
    store.selectedTileForDiscard = null;
    if(elements.selectedTileDisplayEl) {
        elements.selectedTileDisplayEl.textContent = "Selected Tile: None";
    }
    
    store.currentGameInfo.current_player_id = result.next_player_id;
    store.currentGameInfo.winner_found = result.winner_found;

    store.discardedTiles.push(result.discarded_tile);
    displayDiscardedTiles();
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
