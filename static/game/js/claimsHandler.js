import { processAiTurns } from './aiTurnHandler.js';
import { showCelebrationScreen } from './celebrationScreen.js';
import { elements, store } from './gameStore.js';
import { displayHand, displayRevealedSets } from './tileDisplay.js';

export function showClaimPrompt(tile, claimType) {
    store.activeClaimType = claimType;
    elements.playerConsoleEl.textContent =
        `Player discarded ${tile.suit} ${tile.value}. Do you want to claim ${claimType}?`;

    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
    if (elements.btnClaimNo) elements.btnClaimNo.disabled = false;
    if (elements.btnClaimYes) elements.btnClaimYes.disabled = false;
}

export function hideClaimPrompt() {
    if (elements.btnClaimNo) elements.btnClaimNo.disabled = true;
    if (elements.btnClaimYes) elements.btnClaimYes.disabled = true;
}

export async function handleClaimYes() {
    if (store.activeClaimType === 'PUNG') {
        await handleClaimPungYes();
    } else if (store.activeClaimType === 'KONG') {
        await handleClaimKongYes();
    } else if (store.activeClaimType === 'WIN') {
        await handleClaimWinYes();
    }
}

export async function handleClaimNo() {
    if (store.activeClaimType === 'PUNG') {
        await handleClaimPungNo();
    } else if (store.activeClaimType === 'KONG') {
        await handleClaimKongNo();
    } else if (store.activeClaimType === 'WIN') {
        await handleClaimWinNo();
    }
}

export async function handleClaimPungYes() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch('/api/player_claims_pung', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: true })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (result && result.success) {
        handleSuccessfulClaim(result);
    } else {
        handleFailedPungClaim(result);
    }
}

export async function handleClaimPungNo() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch('/api/player_claims_pung', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: false })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message;
    }

    if (result && result.success && result.action === "claim_declined") {
        handleClaimDeclined(result);
    } else {
        if (result?.winner_found !== undefined) {
            store.currentGameInfo.winner_found = result.winner_found;
        }
    }
}

export async function handleClaimKongYes() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch('/api/player_claims_kong', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: true })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (result && result.success) {
        handleSuccessfulKongClaim(result);
    } else {
        handleFailedKongClaim(result);
    }
}

export async function handleClaimKongNo() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch('/api/player_claims_kong', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: false })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (result && result.success && result.action === "claim_declined") {
        handleClaimDeclined(result);
    }
}

function handleSuccessfulClaim(result) {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message;
    }
    displayHand(result.player_hand);
    displayRevealedSets(result.revealed_sets);

    store.currentGameInfo.winner_found = result.winner_found;
    store.currentGameInfo.winning_player_id = result.winning_player_id;

    if (store.currentGameInfo.winner_found) {
        handleWinAfterClaim();
    } else if (result.action === "discard_after_pung") {
        enableDiscardAfterClaim();
    }
}

function handleFailedPungClaim(result) {
    if (elements.playerConsoleEl && result) {
        elements.playerConsoleEl.textContent = "Error claiming Pung: " + (result.message || "Unknown");
    }
    if (result?.winner_found !== undefined) {
        store.currentGameInfo.winner_found = result.winner_found;
    }
}

function handleClaimDeclined(result) {
    store.currentGameInfo.current_player_id = result.next_player_id;
    store.currentGameInfo.winner_found = result.winner_found;
    store.currentGameInfo.winning_player_id = result.winning_player_id;

    updateGameInfoAfterDecline(result);

    if (store.currentGameInfo.winner_found) {
        handleWinAfterClaimDecline();
    } else if (result.next_player_id !== 0) {
        processAiTurns();
    } else {
        enableHumanTurn();
    }
}

function handleWinAfterClaim() {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent =
            `Player ${store.currentGameInfo.winning_player_id} WINS! (After Pung claim processing path)`;
    }
    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
}

function handleWinAfterClaimDecline() {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent =
            `Player ${store.currentGameInfo.winning_player_id} WINS! (After claim decline processing path)`;
    }
    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
}

function enableDiscardAfterClaim() {
    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = false;
}

export function enableHumanTurn() {
    if (elements.btnDrawTile) elements.btnDrawTile.disabled = false;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
}

function updateGameInfoAfterDecline(result) {
    if (elements.gameInfoEl && result.next_player_id !== undefined && result.discarded_tile) {
        elements.gameInfoEl.innerHTML = `
            Wind: ${store.currentGameInfo.game_wind || 'N/A'}<br> 
        `;
    }
}

async function handleClaimWinYes() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch('/api/player_claims_win', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: true })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (result && result.success) {
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = result.message;
        }
        store.currentGameInfo.winner_found = result.winner_found;
        store.currentGameInfo.winning_player_id = result.winning_player_id;

        if (result.action === "win_claimed") {
            showCelebrationScreen(result.winning_player_id);
        }

        if (result.hand) {
            displayHand(result.hand);
        }
        if (result.revealed_sets) {
            displayRevealedSets(result.revealed_sets);
        }
    } else {
        handleFailedClaim(result);
    }
}

async function handleClaimWinNo() {
    if (store.currentGameInfo.winner_found) return;

    const response = await fetch('/api/player_claims_win', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm_claim: false })
    });
    const result = await response.json();
    hideClaimPrompt();

    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message;
    }

    if (result && result.success && result.action === "claim_declined") {
        handleClaimDeclined(result);
    }
}

function handleSuccessfulWinClaim(result) {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message || `Player ${result.winning_player_id} WINS!`;
    }
    if (result.hand) displayHand(result.hand);
    if (result.revealed_sets) displayRevealedSets(result.revealed_sets);

    store.currentGameInfo.winner_found = result.winner_found;
    store.currentGameInfo.winning_player_id = result.winning_player_id;

    if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;
    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
}

function handleFailedWinClaim(result) {
    if (elements.playerConsoleEl && result) {
        elements.playerConsoleEl.textContent = "Error claiming Win: " + (result.message || "Unknown error");
    }
    if (result?.winner_found !== undefined) {
        store.currentGameInfo.winner_found = result.winner_found;
    }
}

function handleSuccessfulKongClaim(result) {
    if (elements.playerConsoleEl) {
        elements.playerConsoleEl.textContent = result.message;
    }
    displayHand(result.hand);
    displayRevealedSets(result.revealed_sets);

    store.currentGameInfo.winner_found = result.winner_found;
    store.currentGameInfo.winning_player_id = result.winning_player_id;

    if (store.currentGameInfo.winner_found) {
        handleWinAfterClaim();
    } else {
        enableDiscardAfterClaim();
    }
}

function handleFailedKongClaim(result) {
    if (elements.playerConsoleEl && result) {
        elements.playerConsoleEl.textContent = "Error claiming Kong: " + (result.message || "Unknown");
    }
    if (result?.winner_found !== undefined) {
        store.currentGameInfo.winner_found = result.winner_found;
    }
}

