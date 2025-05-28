import { store, elements } from './js/gameStore.js';
import { displayDiscardedTiles } from './js/tileDisplay.js';
import { handleDrawTile, handleDiscardTile, handleReset } from './js/gameActions.js';
import { handleClaimYes, handleClaimNo } from './js/claimsHandler.js';


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
        elements.btnClaimYes.onclick = handleClaimYes;
    }

    if (elements.btnClaimNo) {
        elements.btnClaimNo.onclick = handleClaimNo;
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
    if ((event.key === 'd' || event.key === 'D') && !event.repeat) {
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
