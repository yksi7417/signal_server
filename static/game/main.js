import { openBugReport } from './js/bugReport.js';
import { handleClaimNo, handleClaimYes } from './js/claimsHandler.js';
import { handleDiscardTile, handleDrawTile, handleReset } from './js/gameActions.js';
import { elements, store } from './js/gameStore.js';
import { displayDiscardedTiles, selectTileByIndex } from './js/tileDisplay.js';


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

    const btnBugReport = document.getElementById('btnBugReport');
    if (btnBugReport) {
        btnBugReport.onclick = openBugReport;
    }
}


// Initialize discard timer slider from localStorage
function initializeTimerSlider() {
    const slider = document.getElementById('discardTimerSlider');
    const valueLabel = document.getElementById('discardTimerValue');
    if (!slider || !valueLabel) return;

    // Load saved value from localStorage
    const saved = localStorage.getItem('discardTimerSeconds');
    if (saved) {
        const seconds = parseInt(saved, 10);
        if (seconds >= 5 && seconds <= 120) {
            slider.value = seconds;
            store.DISCARD_TIMEOUT_MS = seconds * 1000;
        }
    }
    valueLabel.textContent = `${slider.value}s`;

    slider.addEventListener('input', () => {
        const seconds = parseInt(slider.value, 10);
        valueLabel.textContent = `${seconds}s`;
        store.DISCARD_TIMEOUT_MS = seconds * 1000;
        localStorage.setItem('discardTimerSeconds', seconds);
    });
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
    // Skip game hotkeys when typing in text fields (e.g. bug report)
    const tag = event.target.tagName;
    if (tag === 'TEXTAREA' || tag === 'INPUT' || event.target.isContentEditable) {
        return;
    }

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

    // Arrow keys to navigate tile selection
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        if (elements.btnDiscardTile && !elements.btnDiscardTile.disabled && store.currentHandTiles.length > 0) {
            event.preventDefault();
            let idx = store.selectedTileIndex;
            if (idx < 0) idx = 0; // start from left if nothing selected
            else if (event.key === 'ArrowLeft') idx = Math.max(0, idx - 1);
            else idx = Math.min(store.currentHandTiles.length - 1, idx + 1);
            selectTileByIndex(idx);
        }
    }
});

window.onload = () => {
    initializeEventListeners();
    initializeTimerSlider();
    handleReset();
    initializeGame();
};
