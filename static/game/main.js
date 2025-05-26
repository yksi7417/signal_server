import { store, elements } from './js/gameStore.js';
import { displayHand, displayGameInfo, displayRevealedSets } from './js/tileDisplay.js';
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


eel.expose(update_history_js); 
function update_history_js(hist) {
  console.log("Python called update_history_js with:", hist);
}

window.onload = () => {
  initializeEventListeners();
  handleReset();
};
