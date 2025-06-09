import { handleClaimNo, handleClaimYes } from './js/claimsHandler.js';
import { handleDiscardTile, handleDrawTile, handleReset } from './js/gameActions.js';
import { elements, store } from './js/gameStore.js';
import { displayDiscardedTiles } from './js/tileDisplay.js';


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

// Add keyboard controls
document.addEventListener('keydown', (event) => {
    if ((event.key === 'd' || event.key === 'D') && !event.repeat) {
        event.preventDefault(); // Prevent page scrolling

        const yesButton = document.getElementById('btnClaimYes');
        const discardButton = document.getElementById('btnDiscardTile');

        // Priority 1: If a claim prompt is active, trigger the Yes button
        if (yesButton && !yesButton.disabled) {
            yesButton.click();
        }
        // Priority 2: If discard is enabled and a tile is selected, discard it
        else if (discardButton && !discardButton.disabled && store.selectedTileForDiscard) {
            discardButton.click();
        } else if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = "Select a tile to discard first, or wait for your turn.";
        }
    }
});

window.onload = () => {
    initializeEventListeners();
    handleReset();
    initializeGame();
};
