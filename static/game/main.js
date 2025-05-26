// cache DOM nodes
const btnReset = document.getElementById('reset');
const gameInfoEl = document.getElementById('game-info');
const playerHandEl = document.getElementById('player-hand');
const btnDrawTile = document.getElementById('btnDrawTile');
const btnDiscardTile = document.getElementById('btnDiscardTile');
const playerConsoleEl = document.getElementById('player-console'); // For messages
const selectedTileDisplayEl = document.getElementById('selected-tile-display');
const claimPromptEl = document.getElementById('claim-prompt');
const claimMessageEl = document.getElementById('claim-message');
const btnClaimYes = document.getElementById('btnClaimYes');
const btnClaimNo = document.getElementById('btnClaimNo');
const revealedSetsEl = document.getElementById('revealed-sets-display');


let selectedTileForDiscard = null; // To store which tile object the player clicked on
let currentHandTiles = []; // To store the current hand of Tile objects {suit, value}
const INIT_HAND_SIZE = 13; // Define INIT_HAND_SIZE in JS 
let current_game_info = {}; // Store global game info from backend


btnReset.onclick = async () => {
  await eel.reset_game()(); 
  console.log("Game reset on backend. Reloading initial state...");
  loadInitialGameState(); 
  if(playerConsoleEl) playerConsoleEl.textContent = "Game reset. New game started.";
  if(selectedTileDisplayEl) selectedTileDisplayEl.textContent = "Selected Tile: None";
  selectedTileForDiscard = null;
  display_revealed_sets([]); 
  hideClaimPrompt(); 
  if(current_game_info) current_game_info.winner_found = false; // Reset global win state
  // Re-enable buttons if they were disabled by a win
  if(btnDrawTile) btnDrawTile.disabled = false;
  if(btnDiscardTile) btnDiscardTile.disabled = true; // Standard start state
};


function showClaimPrompt(tile, claimType) {
    if (!claimPromptEl || !claimMessageEl) return;
    claimMessageEl.textContent = `Player discarded ${tile.suit} ${tile.value}. Do you want to claim ${claimType}?`;
    claimPromptEl.style.display = 'block';
    if(btnDrawTile) btnDrawTile.disabled = true;
    if(btnDiscardTile) btnDiscardTile.disabled = true;
}

function hideClaimPrompt() {
    if (!claimPromptEl) return;
    claimPromptEl.style.display = 'none';
    // Button re-enabling is handled by specific logic flows after claim decision or game state update
}


function display_revealed_sets(revealed_sets_data) { 
    if (!revealedSetsEl) return;
    if (!revealed_sets_data || revealed_sets_data.length === 0) {
        revealedSetsEl.textContent = "Revealed Sets: None";
        return;
    }
    let html = "Revealed Sets: ";
    revealed_sets_data.forEach(meld => {
        const tilesString = meld.tiles.map(t => `${t.suit} ${t.value}`).join(', ');
        html += `${meld.type} (${tilesString}) | `;
    });
    revealedSetsEl.innerHTML = html;
}


function display_hand(tiles) {
  if (!playerHandEl) return;
  currentHandTiles = tiles || []; 
  if (currentHandTiles.length === 0) {
    playerHandEl.textContent = "No tiles in hand.";
    return;
  }
  
  playerHandEl.innerHTML = ''; 
  currentHandTiles.forEach((tile, index) => {
    const tileEl = document.createElement('span');
    tileEl.textContent = `${tile.suit} ${tile.value}`;
    tileEl.style.border = "1px solid #ccc";
    tileEl.style.padding = "5px";
    tileEl.style.margin = "2px";
    tileEl.style.cursor = "pointer";
    tileEl.onclick = () => {
      if (current_game_info.winner_found) return; // Don't allow selection if game is over
      if (currentHandTiles.length === INIT_HAND_SIZE + 1 && !btnDiscardTile.disabled) { 
        selectedTileForDiscard = tile; 
        if(selectedTileDisplayEl) selectedTileDisplayEl.textContent = `Selected Tile: ${tile.suit} ${tile.value}`;
        document.querySelectorAll('#player-hand span').forEach(el => el.style.backgroundColor = 'transparent');
        tileEl.style.backgroundColor = 'lightblue';
      } else {
         if(playerConsoleEl && !btnDiscardTile.disabled) playerConsoleEl.textContent = "Draw a tile first or ensure it's your turn to discard.";
         else if (playerConsoleEl && btnDiscardTile.disabled && !btnDrawTile.disabled) playerConsoleEl.textContent = "Draw a tile first.";
      }
    };
    playerHandEl.appendChild(tileEl);
    if (index < currentHandTiles.length - 1) {
      playerHandEl.appendChild(document.createTextNode(' | '));
    }
  });
}

function display_game_info(info) {
  if (!gameInfoEl) return;
  if (!info) {
    gameInfoEl.textContent = "";
    return;
  }
  gameInfoEl.innerHTML = `
    Game Wind: ${info.game_wind || 'N/A'}<br>
    Current Player ID: ${info.current_player_id !== undefined ? info.current_player_id : 'N/A'}
  `;
  if(info) current_game_info = {...current_game_info, ...info}; // Merge new info into global, preserving winner_found if not in 'info'
}

eel.expose(update_history_js); 
function update_history_js(hist) {
  console.log("Python called update_history_js with:", hist);
}

if (btnDrawTile) {
  btnDrawTile.onclick = async () => {
    if(playerConsoleEl) playerConsoleEl.textContent = "";
    if (current_game_info.winner_found) {
        if(playerConsoleEl) playerConsoleEl.textContent = `Game over. Player ${current_game_info.winning_player_id} has won. Please reset.`;
        return;
    }
    try {
      const result = await eel.eel_draw_tile()();
      if (result && result.success) {
        current_game_info.winner_found = result.winner_found; // Update global win status
        current_game_info.winning_player_id = result.winning_player_id;

        display_hand(result.hand); 
        
        if (result.action === "win" && result.winner_found) { 
            if(playerConsoleEl) playerConsoleEl.textContent = `Congratulations! Player ${result.winning_player_id} WINS by self-draw with ${result.drawn_tile.suit} ${result.drawn_tile.value}!`;
            if(result.revealed_sets) display_revealed_sets(result.revealed_sets);
            if(btnDrawTile) btnDrawTile.disabled = true;
            if(btnDiscardTile) btnDiscardTile.disabled = true;
            hideClaimPrompt();
        } else if (!result.winner_found) { 
            if(playerConsoleEl) playerConsoleEl.textContent = `Drew: ${result.drawn_tile.suit} ${result.drawn_tile.value}. You now have 14 tiles. Select one to discard.`;
            if(btnDrawTile) btnDrawTile.disabled = true;
            if(btnDiscardTile) btnDiscardTile.disabled = false;
        }
      } else { 
        if(playerConsoleEl && result) playerConsoleEl.textContent = "Error drawing tile: " + (result.error || "Unknown error");
        if(result && result.winner_found !== undefined) current_game_info.winner_found = result.winner_found; 
      }
    } catch (error) {
      console.error("Error calling eel_draw_tile:", error);
      if(playerConsoleEl) playerConsoleEl.textContent = "Exception drawing tile: " + error;
    }
  };
}

if (btnDiscardTile) {
  btnDiscardTile.onclick = async () => {
    if (current_game_info.winner_found) {
        if(playerConsoleEl) playerConsoleEl.textContent = `Game over. Player ${current_game_info.winning_player_id} has won. Please reset.`;
        return;
    }
    if (!selectedTileForDiscard) {
      if(playerConsoleEl) playerConsoleEl.textContent = "Please select a tile from your hand to discard.";
      return;
    }
    if(playerConsoleEl) playerConsoleEl.textContent = "";
    try {
      const result = await eel.eel_discard_tile(selectedTileForDiscard)();
      if (result && result.success) {
        display_hand(result.updated_hand);
        if(playerConsoleEl) playerConsoleEl.textContent = `Discarded ${selectedTileForDiscard.suit} ${selectedTileForDiscard.value}.`;
        selectedTileForDiscard = null;
        if(selectedTileDisplayEl) selectedTileDisplayEl.textContent = "Selected Tile: None";
        
        current_game_info.current_player_id = result.next_player_id; 
        current_game_info.winner_found = result.winner_found; 

        if (result.human_can_claim_pung && !current_game_info.winner_found) { 
            showClaimPrompt(result.claimable_tile, "PUNG");
        } else if (current_game_info.winner_found) { 
            if(playerConsoleEl) playerConsoleEl.textContent = `Game over! Player ${current_game_info.winning_player_id} has won! (Noted after your discard)`;
            if(btnDrawTile) btnDrawTile.disabled = true;
            if(btnDiscardTile) btnDiscardTile.disabled = true;
        } else if (result.next_player_id !== 0) { 
            if (gameInfoEl && result.next_player_id !== undefined && result.last_discarded_tile) {
                 gameInfoEl.innerHTML = `Game Wind: ${current_game_info.game_wind || 'N/A'}<br>
                                   Current Player ID: ${result.next_player_id}<br>
                                   Last Discard: ${result.last_discarded_tile.suit} ${result.last_discarded_tile.value}`;
            }
            processAiTurns();
        } else { // Next is human (Player 0) and no win
            if(btnDrawTile) btnDrawTile.disabled = false;
            if(btnDiscardTile) btnDiscardTile.disabled = true;
             if (gameInfoEl && result.next_player_id !== undefined && result.last_discarded_tile) {
                 gameInfoEl.innerHTML = `Game Wind: ${current_game_info.game_wind || 'N/A'}<br>
                                   Current Player ID: ${result.next_player_id}<br>
                                   Last Discard: ${result.last_discarded_tile.suit} ${result.last_discarded_tile.value}`;
            }
        }
      } else {
        if(playerConsoleEl && result) playerConsoleEl.textContent = "Error discarding tile: " + (result.error || "Unknown error");
        if (result && result.hand) display_hand(result.hand);
        if(result && result.winner_found !== undefined) current_game_info.winner_found = result.winner_found;
      }
    } catch (error) {
      console.error("Error calling eel_discard_tile:", error);
      if(playerConsoleEl) playerConsoleEl.textContent = "Exception discarding tile: " + error;
    }
  };
}


if (btnClaimYes) {
    btnClaimYes.onclick = async () => {
        if (current_game_info.winner_found) return;
        const result = await eel.eel_player_claims_pung(true)();
        hideClaimPrompt();
        if (result && result.success) {
            if (playerConsoleEl) playerConsoleEl.textContent = result.message;
            display_hand(result.player_hand);
            display_revealed_sets(result.revealed_sets); 
            current_game_info.winner_found = result.winner_found; 
            current_game_info.winning_player_id = result.winning_player_id; // Will be null if no win

            if (current_game_info.winner_found) {
                 if(playerConsoleEl) playerConsoleEl.textContent = `Player ${current_game_info.winning_player_id} WINS! (After Pung claim processing path)`;
                 if(btnDrawTile) btnDrawTile.disabled = true;
                 if(btnDiscardTile) btnDiscardTile.disabled = true;
            } else if (result.action === "discard_after_pung") {
                if(btnDrawTile) btnDrawTile.disabled = true;
                if(btnDiscardTile) btnDiscardTile.disabled = false; 
            }
        } else {
            if (playerConsoleEl && result) playerConsoleEl.textContent = "Error claiming Pung: " + (result.message || "Unknown");
            if(result && result.winner_found !== undefined) current_game_info.winner_found = result.winner_found;
        }
    };
}

if (btnClaimNo) {
    btnClaimNo.onclick = async () => {
        if (current_game_info.winner_found) return;
        const result = await eel.eel_player_claims_pung(false)();
        hideClaimPrompt();
        if (playerConsoleEl) playerConsoleEl.textContent = result.message;
        if (result && result.success && result.action === "claim_declined") {
            current_game_info.current_player_id = result.next_player_id; 
            current_game_info.winner_found = result.winner_found; 
            current_game_info.winning_player_id = result.winning_player_id;

            if (gameInfoEl && result.next_player_id !== undefined && result.last_discarded_tile) {
                gameInfoEl.innerHTML = `Game Wind: ${current_game_info.game_wind || 'N/A'}<br> 
                                  Current Player ID: ${result.next_player_id}<br>
                                  Last Discard: ${result.last_discarded_tile.suit} ${result.last_discarded_tile.value}`;
            }
            
            if (current_game_info.winner_found) {
                 if(playerConsoleEl) playerConsoleEl.textContent = `Player ${current_game_info.winning_player_id} WINS! (Noted after claim declined path)`;
                 if(btnDrawTile) btnDrawTile.disabled = true;
                 if(btnDiscardTile) btnDiscardTile.disabled = true;
            } else if (result.next_player_id !== 0) { 
                processAiTurns();
            } else { // Next is human and no win
                if(btnDrawTile) btnDrawTile.disabled = false;
                if(btnDiscardTile) btnDiscardTile.disabled = true;
            }
        } else {
             if(result && result.winner_found !== undefined) current_game_info.winner_found = result.winner_found;
        }
    };
}

async function processAiTurns() {
    if (!current_game_info || current_game_info.current_player_id === undefined) {
        console.log("Waiting for game state...");
        return;
    }
    if (current_game_info.winner_found) { 
        console.log("Game already won, skipping AI turns.");
        if (playerConsoleEl) playerConsoleEl.textContent = `Game over. Player ${current_game_info.winning_player_id} has won. Please reset.`;
        if(btnDrawTile) btnDrawTile.disabled = true;
        if(btnDiscardTile) btnDiscardTile.disabled = true;
        return;
    }

    let next_player_is_ai = current_game_info.current_player_id !== 0; 

    while (next_player_is_ai && !current_game_info.winner_found) { 
        if (playerConsoleEl) playerConsoleEl.textContent = `Player ${current_game_info.current_player_id} (AI) is thinking...`;
        
        if(btnDrawTile) btnDrawTile.disabled = true;
        if(btnDiscardTile) btnDiscardTile.disabled = true;
        hideClaimPrompt();

        try {
            const ai_turn_result = await eel.eel_request_ai_turn()();
            current_game_info.winner_found = ai_turn_result.winner_found; 
            current_game_info.winning_player_id = ai_turn_result.winning_player_id;

            if (ai_turn_result && ai_turn_result.success) {
                if(ai_turn_result.player0_hand) display_hand(ai_turn_result.player0_hand);
                if(ai_turn_result.player0_revealed_sets) display_revealed_sets(ai_turn_result.player0_revealed_sets);

                if (ai_turn_result.action === "win" && ai_turn_result.winner_found) { // AI won on its draw
                    if(playerConsoleEl) playerConsoleEl.textContent = `AI Player ${ai_turn_result.winning_player_id} WINS by self-draw with ${ai_turn_result.drawn_tile_for_win.suit} ${ai_turn_result.drawn_tile_for_win.value}!`;
                    if(gameInfoEl) gameInfoEl.innerHTML += `<br><b>Player ${ai_turn_result.winning_player_id} WINS!</b>`;
                    // Buttons already disabled by loop start. No further AI turns.
                    return; 
                }
                
                if (ai_turn_result.discarded_tile) { // AI discarded (not won)
                    if (playerConsoleEl) playerConsoleEl.textContent = `AI Player ${ai_turn_result.ai_player_id} discarded ${ai_turn_result.discarded_tile.suit} ${ai_turn_result.discarded_tile.value}.`;
                    current_game_info.current_player_id = ai_turn_result.next_player_id; 
                    if(gameInfoEl && current_game_info.game_wind){ 
                        gameInfoEl.innerHTML = `Game Wind: ${current_game_info.game_wind}<br>
                                        Current Player ID: ${current_game_info.current_player_id}<br>
                                        Last Discard (AI): ${ai_turn_result.discarded_tile.suit} ${ai_turn_result.discarded_tile.value}`;
                    }

                    if (ai_turn_result.human_can_claim_pung && !current_game_info.winner_found) { 
                        showClaimPrompt(ai_turn_result.claimable_tile, "PUNG");
                        return; 
                    }
                } // else if AI turn result didn't have a discard (e.g. error before discard)
                
                next_player_is_ai = ai_turn_result.next_player_id !== 0;
                if (!next_player_is_ai && !current_game_info.winner_found) { 
                    if (playerConsoleEl) playerConsoleEl.textContent += " Your turn!";
                    if(btnDrawTile) btnDrawTile.disabled = false;
                    if(btnDiscardTile) btnDiscardTile.disabled = true;
                }
            } else { // AI turn was not successful 
                if (playerConsoleEl && ai_turn_result && ai_turn_result.error) playerConsoleEl.textContent = "AI turn issue: " + ai_turn_result.error;
                else if (playerConsoleEl && !current_game_info.winner_found) playerConsoleEl.textContent = "Waiting for your action.";

                if(ai_turn_result && ai_turn_result.player0_hand) display_hand(ai_turn_result.player0_hand);
                if(ai_turn_result && ai_turn_result.player0_revealed_sets) display_revealed_sets(ai_turn_result.player0_revealed_sets);
                
                if(current_game_info.winner_found){ 
                     if(playerConsoleEl) playerConsoleEl.textContent = `Player ${current_game_info.winning_player_id} WINS! (Noted during AI turn error path)`;
                     if(gameInfoEl && current_game_info.winning_player_id !== undefined) gameInfoEl.innerHTML += `<br><b>Player ${current_game_info.winning_player_id} WINS!</b>`;
                     if(btnDrawTile) btnDrawTile.disabled = true;
                     if(btnDiscardTile) btnDiscardTile.disabled = true;
                } else if(ai_turn_result && ai_turn_result.human_can_claim_pung){ 
                    showClaimPrompt(ai_turn_result.claimable_tile, "PUNG");
                } else if (!current_game_info.winner_found) { 
                     if(btnDrawTile) btnDrawTile.disabled = false; 
                     if(btnDiscardTile) btnDiscardTile.disabled = true;
                }
                return; 
            }
        } catch (error) {
            console.error("Error during AI turn processing:", error);
            if (playerConsoleEl) playerConsoleEl.textContent = "Error processing AI turn.";
            return; 
        }
        
        if (next_player_is_ai && !current_game_info.winner_found) { 
            await new Promise(resolve => setTimeout(resolve, 500)); 
        }
    }
     // If loop finishes because winner_found became true mid-loop by an AI
    if (current_game_info.winner_found) {
        if (playerConsoleEl) playerConsoleEl.textContent = `Game over. Player ${current_game_info.winning_player_id} has won. Please reset.`;
        if(gameInfoEl && current_game_info.winning_player_id !== undefined) gameInfoEl.innerHTML += `<br><b>Player ${current_game_info.winning_player_id} WINS!</b>`;
        if(btnDrawTile) btnDrawTile.disabled = true;
        if(btnDiscardTile) btnDiscardTile.disabled = true;
    }
}


// New startup logic
async function loadInitialGameState() {
  console.log("Requesting new game state from Python...");
  try {
    const game_info_data = await eel.start_new_game()(); 
    if (game_info_data) {
      console.log("Received game state:", game_info_data);
      current_game_info = game_info_data; // This includes winner_found: false
      display_hand(current_game_info.player_hand);
      display_game_info(current_game_info); 
      display_revealed_sets([]); 
      hideClaimPrompt(); 
      
      if (current_game_info.winner_found) { // Should be false from start_new_game
         if(playerConsoleEl) playerConsoleEl.textContent = `Game over. Player ${current_game_info.winning_player_id} has won. Please reset.`;
         if(gameInfoEl && current_game_info.winning_player_id !== undefined) gameInfoEl.innerHTML += `<br><b>Player ${current_game_info.winning_player_id} WINS!</b>`;
         if(btnDrawTile) btnDrawTile.disabled = true;
         if(btnDiscardTile) btnDiscardTile.disabled = true;
      } else if (current_game_info.current_player_id !== 0) { 
          processAiTurns();
      } else { // Player 0's turn and no winner
          if(btnDrawTile) btnDrawTile.disabled = false;
          if(btnDiscardTile) btnDiscardTile.disabled = true;
          if(playerConsoleEl) playerConsoleEl.textContent = "Game loaded. Your turn to draw.";
      }
    } else {
      console.error("Did not receive game info from backend.");
      if (playerHandEl) playerHandEl.textContent = "Error loading game.";
      if(playerConsoleEl) playerConsoleEl.textContent = "Error loading game from backend.";
    }
  } catch (error) {
    console.error("Error starting new game:", error);
    if (playerHandEl) playerHandEl.textContent = "Error connecting to backend.";
    if(playerConsoleEl) playerConsoleEl.textContent = "Error connecting to backend to start game.";
  }
}

// Initial load
window.onload = () => {
    loadInitialGameState();
};
// Modify btnDiscardTile.onclick to integrate processAiTurns
if (btnDiscardTile) {
  btnDiscardTile.onclick = async () => {
    if (current_game_info.winner_found) {
        if(playerConsoleEl) playerConsoleEl.textContent = `Game over. Player ${current_game_info.winning_player_id} has won. Please reset.`;
        return;
    }
    if (!selectedTileForDiscard) {
      if(playerConsoleEl) playerConsoleEl.textContent = "Please select a tile from your hand to discard.";
      return;
    }
    if(playerConsoleEl) playerConsoleEl.textContent = "";
    try {
      const result = await eel.eel_discard_tile(selectedTileForDiscard)();
      if (result && result.success) {
        display_hand(result.updated_hand);
        if(playerConsoleEl) playerConsoleEl.textContent = `Discarded ${selectedTileForDiscard.suit} ${selectedTileForDiscard.value}.`;
        selectedTileForDiscard = null;
        if(selectedTileDisplayEl) selectedTileDisplayEl.textContent = "Selected Tile: None";
        
        current_game_info.current_player_id = result.next_player_id; // Update global current player ID
        current_game_info.winner_found = result.winner_found; // Update global win status

        if (result.human_can_claim_pung && !current_game_info.winner_found) { // Check win status
            showClaimPrompt(result.claimable_tile, "PUNG");
        } else if (current_game_info.winner_found) { // Check if discard somehow led to a win (e.g. Robbing the Kong - not implemented)
            if(playerConsoleEl) playerConsoleEl.textContent = `Game over! Player ${current_game_info.winning_player_id} has won!`;
            if(gameInfoEl && current_game_info.winning_player_id !== undefined) gameInfoEl.innerHTML += `<br><b>Player ${current_game_info.winning_player_id} WINS!</b>`;
            if(btnDrawTile) btnDrawTile.disabled = true;
            if(btnDiscardTile) btnDiscardTile.disabled = true;
        } else if (result.next_player_id !== 0) { // If next is AI and no win
            if (gameInfoEl && result.next_player_id !== undefined && result.last_discarded_tile) {
                 gameInfoEl.innerHTML = `Game Wind: ${current_game_info.game_wind || 'N/A'}<br>
                                   Current Player ID: ${result.next_player_id}<br>
                                   Last Discard: ${result.last_discarded_tile.suit} ${result.last_discarded_tile.value}`;
            }
            processAiTurns();
        } else { // Next is human (Player 0) and no win
            if(btnDrawTile) btnDrawTile.disabled = false;
            if(btnDiscardTile) btnDiscardTile.disabled = true;
            if (gameInfoEl && result.next_player_id !== undefined && result.last_discarded_tile) {
                 gameInfoEl.innerHTML = `Game Wind: ${current_game_info.game_wind || 'N/A'}<br>
                                   Current Player ID: ${result.next_player_id}<br>
                                   Last Discard: ${result.last_discarded_tile.suit} ${result.last_discarded_tile.value}`;
            }
        }
      } else {
        if(playerConsoleEl && result) playerConsoleEl.textContent = "Error discarding tile: " + (result.error || "Unknown error");
         if (result && result.hand) { 
            display_hand(result.hand);
        }
        if(result && result.winner_found !== undefined) current_game_info.winner_found = result.winner_found;
      }
    } catch (error) {
      console.error("Error calling eel_discard_tile:", error);
      if(playerConsoleEl) playerConsoleEl.textContent = "Exception discarding tile: " + error;
    }
  };
}
