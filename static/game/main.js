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


// call Python reset_game()
btnReset.onclick = async () => {
  await eel.reset_game()(); 
  console.log("Game reset on backend. Reloading initial state...");
  loadInitialGameState(); // This will now also set initial button states
  // Clear console and selection
  if(playerConsoleEl) playerConsoleEl.textContent = "Game reset. Click 'Reset' or reload for new hand.";
  if(selectedTileDisplayEl) selectedTileDisplayEl.textContent = "Selected Tile: None";
  selectedTileForDiscard = null;
  display_revealed_sets([]); // Clear revealed sets on UI
  hideClaimPrompt(); // Ensure claim prompt is hidden on reset
};


function showClaimPrompt(tile, claimType) {
    if (!claimPromptEl || !claimMessageEl) return;
    claimMessageEl.textContent = `Player discarded ${tile.suit} ${tile.value}. Do you want to claim ${claimType}?`;
    claimPromptEl.style.display = 'block';
    // Disable game actions while prompt is visible
    if(btnDrawTile) btnDrawTile.disabled = true;
    if(btnDiscardTile) btnDiscardTile.disabled = true;
}

function hideClaimPrompt() {
    if (!claimPromptEl) return;
    claimPromptEl.style.display = 'none';
    // Re-enable game actions as appropriate after decision (handled by specific logic)
}


function display_revealed_sets(revealed_sets_data) { // Renamed parameter to avoid conflict
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
  currentHandTiles = tiles || []; // Store the hand
  if (currentHandTiles.length === 0) {
    playerHandEl.textContent = "No tiles in hand.";
    return;
  }
  
  playerHandEl.innerHTML = ''; // Clear previous tiles
  currentHandTiles.forEach((tile, index) => {
    const tileEl = document.createElement('span');
    tileEl.textContent = `${tile.suit} ${tile.value}`;
    tileEl.style.border = "1px solid #ccc";
    tileEl.style.padding = "5px";
    tileEl.style.margin = "2px";
    tileEl.style.cursor = "pointer";
    tileEl.onclick = () => {
      // Only allow selection if hand size suggests ready for discard (e.g. 14 tiles)
      if (currentHandTiles.length === INIT_HAND_SIZE + 1) { // INIT_HAND_SIZE needs to be available in JS
        selectedTileForDiscard = tile; // tile is {suit, value}
        if(selectedTileDisplayEl) selectedTileDisplayEl.textContent = `Selected Tile: ${tile.suit} ${tile.value}`;
        // Highlight selected tile visually (optional)
        document.querySelectorAll('#player-hand span').forEach(el => el.style.backgroundColor = 'transparent');
        tileEl.style.backgroundColor = 'lightblue';
      } else {
         if(playerConsoleEl) playerConsoleEl.textContent = "Draw a tile first to have 14 tiles, then select one to discard.";
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
  // Store game_info globally
  if(info) current_game_info = info;
}

// expose a JS function so Python can push updates to us
eel.expose(update_history_js); 
function update_history_js(hist) {
  console.log("Python called update_history_js with:", hist);
}

if (btnDrawTile) {
  btnDrawTile.onclick = async () => {
    if(playerConsoleEl) playerConsoleEl.textContent = "";
    try {
      const result = await eel.eel_draw_tile()();
      if (result && result.success) {
        display_hand(result.hand);
        if(playerConsoleEl) playerConsoleEl.textContent = `Drew: ${result.drawn_tile.suit} ${result.drawn_tile.value}. You now have 14 tiles. Select one to discard.`;
        btnDrawTile.disabled = true;
        btnDiscardTile.disabled = false;
      } else {
        if(playerConsoleEl) playerConsoleEl.textContent = "Error drawing tile: " + (result ? result.error : "Unknown error");
      }
    } catch (error) {
      console.error("Error calling eel_draw_tile:", error);
      if(playerConsoleEl) playerConsoleEl.textContent = "Exception drawing tile: " + error;
    }
  };
}

if (btnDiscardTile) {
  btnDiscardTile.onclick = async () => {
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
        
        if (result.human_can_claim_pung) {
            showClaimPrompt(result.claimable_tile, "PUNG");
            // Buttons (draw/discard) will be disabled by showClaimPrompt
        } else {
            // No claim for human, or not human's turn to claim.
            // Regular turn advancement, enable draw if it's our turn, disable discard.
            if(btnDrawTile) btnDrawTile.disabled = false; // Or check if it's player 0's turn
            if(btnDiscardTile) btnDiscardTile.disabled = true;
            if(gameInfoEl && result.next_player_id !== undefined && result.last_discarded_tile){
                 // Update current_game_info if you store it globally in JS
                 current_game_info.current_player_id = result.next_player_id; 
                 gameInfoEl.innerHTML = `Game Wind: ${current_game_info.game_wind || 'N/A'}<br>
                                   Current Player ID: ${result.next_player_id}<br>
                                   Last Discard: ${result.last_discarded_tile.suit} ${result.last_discarded_tile.value}`;
            }
        }
      } else {
        if(playerConsoleEl) playerConsoleEl.textContent = "Error discarding tile: " + (result ? result.error : "Unknown error");
         if (result && result.hand) { 
            display_hand(result.hand);
        }
      }
    } catch (error) {
      console.error("Error calling eel_discard_tile:", error);
      if(playerConsoleEl) playerConsoleEl.textContent = "Exception discarding tile: " + error;
    }
  };
}


if (btnClaimYes) {
    btnClaimYes.onclick = async () => {
        const result = await eel.eel_player_claims_pung(true)();
        hideClaimPrompt();
        if (result && result.success) {
            if (playerConsoleEl) playerConsoleEl.textContent = result.message;
            display_hand(result.player_hand);
            display_revealed_sets(result.revealed_sets); 
            if (result.action === "discard_after_pung") {
                if(btnDrawTile) btnDrawTile.disabled = true;
                if(btnDiscardTile) btnDiscardTile.disabled = false; // Player must now discard
            }
        } else {
            if (playerConsoleEl) playerConsoleEl.textContent = "Error claiming Pung: " + (result ? result.message : "Unknown");
        }
    };
}

if (btnClaimNo) {
    btnClaimNo.onclick = async () => {
        const result = await eel.eel_player_claims_pung(false)();
        hideClaimPrompt();
        if (playerConsoleEl) playerConsoleEl.textContent = result.message;
        if (result && result.success && result.action === "claim_declined") {
            current_game_info.current_player_id = result.next_player_id; // Update global state
            if (gameInfoEl && result.next_player_id !== undefined && result.last_discarded_tile) {
                gameInfoEl.innerHTML = `Game Wind: ${current_game_info.game_wind || 'N/A'}<br> 
                                  Current Player ID: ${result.next_player_id}<br>
                                  Last Discard: ${result.last_discarded_tile.suit} ${result.last_discarded_tile.value}`;
            }

            if (result.next_player_id !== 0) { // If next is AI
                processAiTurns();
            } else { // Next is human
                if(btnDrawTile) btnDrawTile.disabled = false;
                if(btnDiscardTile) btnDiscardTile.disabled = true;
            }
        }
    };
}

async function processAiTurns() {
    if (!current_game_info || current_game_info.current_player_id === undefined) {
        console.log("Waiting for game state...");
        return;
    }

    let next_player_is_ai = current_game_info.current_player_id !== 0; 

    while (next_player_is_ai) {
        if (playerConsoleEl) playerConsoleEl.textContent = `Player ${current_game_info.current_player_id} (AI) is thinking...`;
        
        if(btnDrawTile) btnDrawTile.disabled = true;
        if(btnDiscardTile) btnDiscardTile.disabled = true;
        hideClaimPrompt();

        try {
            const ai_turn_result = await eel.eel_request_ai_turn()();
            // console.log("AI turn result:", ai_turn_result);

            if (ai_turn_result && ai_turn_result.success) {
                if (playerConsoleEl) playerConsoleEl.textContent = `AI Player ${ai_turn_result.ai_player_id} discarded ${ai_turn_result.discarded_tile.suit} ${ai_turn_result.discarded_tile.value}.`;
                
                if(ai_turn_result.player0_hand) display_hand(ai_turn_result.player0_hand);
                if(ai_turn_result.player0_revealed_sets) display_revealed_sets(ai_turn_result.player0_revealed_sets);

                current_game_info.current_player_id = ai_turn_result.next_player_id; 
                 if(gameInfoEl && current_game_info.game_wind){ 
                     gameInfoEl.innerHTML = `Game Wind: ${current_game_info.game_wind}<br>
                                       Current Player ID: ${current_game_info.current_player_id}<br>
                                       Last Discard (AI): ${ai_turn_result.discarded_tile.suit} ${ai_turn_result.discarded_tile.value}`;
                 }

                if (ai_turn_result.human_can_claim_pung) {
                    showClaimPrompt(ai_turn_result.claimable_tile, "PUNG");
                    return; 
                }
                
                next_player_is_ai = ai_turn_result.next_player_id !== 0;
                if (!next_player_is_ai) { 
                    if (playerConsoleEl) playerConsoleEl.textContent += " Your turn!";
                    if(btnDrawTile) btnDrawTile.disabled = false;
                    if(btnDiscardTile) btnDiscardTile.disabled = true;
                }
            } else {
                if (playerConsoleEl && ai_turn_result && ai_turn_result.error) playerConsoleEl.textContent = "AI turn issue: " + ai_turn_result.error;
                else if (playerConsoleEl) playerConsoleEl.textContent = "Waiting for your action.";

                if(ai_turn_result && ai_turn_result.player0_hand) display_hand(ai_turn_result.player0_hand);
                if(ai_turn_result && ai_turn_result.player0_revealed_sets) display_revealed_sets(ai_turn_result.player0_revealed_sets);
                
                if(ai_turn_result && ai_turn_result.human_can_claim_pung){ 
                    showClaimPrompt(ai_turn_result.claimable_tile, "PUNG");
                } else {
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
        
        if (next_player_is_ai) { 
            await new Promise(resolve => setTimeout(resolve, 500)); 
        }
    }
}


// New startup logic
async function loadInitialGameState() {
  console.log("Requesting new game state from Python...");
  try {
    const game_info_data = await eel.start_new_game()(); 
    if (game_info_data) {
      console.log("Received game state:", game_info_data);
      current_game_info = game_info_data; 
      display_hand(current_game_info.player_hand);
      display_game_info(current_game_info); 
      display_revealed_sets([]); 
      hideClaimPrompt(); 
      
      if (current_game_info.current_player_id !== 0) { 
          processAiTurns();
      } else {
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

        if (result.human_can_claim_pung) {
            showClaimPrompt(result.claimable_tile, "PUNG");
        } else {
            if (gameInfoEl && result.next_player_id !== undefined && result.last_discarded_tile) {
                 gameInfoEl.innerHTML = `Game Wind: ${current_game_info.game_wind || 'N/A'}<br>
                                   Current Player ID: ${result.next_player_id}<br>
                                   Last Discard: ${result.last_discarded_tile.suit} ${result.last_discarded_tile.value}`;
            }
            if (result.next_player_id !== 0) { // If next is AI
                processAiTurns();
            } else { // Next is human (Player 0)
                if(btnDrawTile) btnDrawTile.disabled = false;
                if(btnDiscardTile) btnDiscardTile.disabled = true;
            }
        }
      } else {
        if(playerConsoleEl) playerConsoleEl.textContent = "Error discarding tile: " + (result ? result.error : "Unknown error");
         if (result && result.hand) { 
            display_hand(result.hand);
        }
      }
    } catch (error) {
      console.error("Error calling eel_discard_tile:", error);
      if(playerConsoleEl) playerConsoleEl.textContent = "Exception discarding tile: " + error;
    }
  };
}
