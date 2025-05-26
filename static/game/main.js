import { store, elements } from './js/gameStore.js';
import { displayHand, displayGameInfo, displayRevealedSets, displayDiscardedTiles } from './js/tileDisplay.js';
import { handleDrawTile, handleDiscardTile, handleReset } from './js/gameActions.js';
import { processAiTurns } from './js/aiTurnHandler.js';
import { handleClaimPungYes, handleClaimPungNo } from './js/claimsHandler.js';


// Initialize button event listeners
function initializeEventListeners() {
    if (elements.btnReset) {
        elements.btnReset.onclick = handleReset;
    }

    if (elements.btnDrawTile) {
        elements.btnDrawTile.onclick = handleDrawTile;
    }

    if (elements.btnDiscardTile) {
        elements.btnDiscardTile.onclick = handleDiscardTile;
    }

    if (elements.btnClaimYes) {
        elements.btnClaimYes.onclick = handleClaimPungYes;
    }

    if (elements.btnClaimNo) {
        elements.btnClaimNo.onclick = handleClaimPungNo;
    }
}


// Initialize game state
async function initializeGame() {
    try {
        store.discardedTiles = [];
        displayDiscardedTiles();
    } catch (error) {
        console.error('Error initializing game:', error);
    }
}

eel.expose(update_history_js); 
function update_history_js(hist) {
  console.log("Python called update_history_js with:", hist);
}

// Add keyboard controls
document.addEventListener('keydown', (event) => {
    // Only handle spacebar press and prevent default space behavior
    if (event.code === 'Space' && !event.repeat) {
        event.preventDefault(); // Prevent page scrolling
        
        const drawButton = document.getElementById('btnDrawTile');
        const discardButton = document.getElementById('btnDiscardTile');
        
        // If discard is enabled and a tile is selected, discard it
        if (discardButton && !discardButton.disabled && store.selectedTileForDiscard) {
            discardButton.click();
        }
        // Otherwise, if draw is enabled, draw a tile
        else if (drawButton && !drawButton.disabled) {
            drawButton.click();
        }
    }
});

window.onload = () => {
  initializeEventListeners();
  handleReset();
  initializeGame();
};
