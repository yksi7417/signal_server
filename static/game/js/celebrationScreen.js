import { elements, store } from './gameStore.js';
import { openBugReport } from './bugReport.js';

// Re-use the spritesheet mapping from tileDisplay.js
const UNICODE_TO_TILE_ID = {};
for (let i = 0; i <= 3; i++) UNICODE_TO_TILE_ID[0x1F000 + i] = 27 + i;
UNICODE_TO_TILE_ID[0x1F004] = 32;
UNICODE_TO_TILE_ID[0x1F005] = 31;
UNICODE_TO_TILE_ID[0x1F006] = 33;
for (let i = 0; i <= 8; i++) UNICODE_TO_TILE_ID[0x1F007 + i] = 9 + i;
for (let i = 0; i <= 8; i++) UNICODE_TO_TILE_ID[0x1F010 + i] = i;
for (let i = 0; i <= 8; i++) UNICODE_TO_TILE_ID[0x1F019 + i] = 18 + i;

function createCelebrationTile(tile) {
    const tileId = tile ? UNICODE_TO_TILE_ID[tile.codePointAt(0)] ?? -1 : -1;
    const el = document.createElement('div');
    el.className = 'tile-img tile-img-discard';
    if (tileId >= 0) {
        const col = tileId % 9;
        const row = Math.floor(tileId / 9);
        el.style.setProperty('--col', col);
        el.style.setProperty('--row', row);
    }
    return el;
}

export function showCelebrationScreen(player_id) {
    // Create celebration overlay if it doesn't exist
    if (!elements.celebrationOverlay) {
        const overlay = document.createElement('div');
        overlay.id = 'celebrationOverlay';
        overlay.style.display = 'none';
        overlay.innerHTML = `
            <div class="celebration-content">
                <h1>WINNER!</h1>
                <h2 id="celebrationMessage"></h2>
                <div id="winningHandDisplay"></div>
                <button id="btnNewGame">Start New Game</button>
                <button id="btnCelebrationBugReport">Report Bug</button>
            </div>
        `;
        document.body.appendChild(overlay);
        elements.celebrationOverlay = overlay;
        document.getElementById('btnNewGame').onclick = async () => {
            await fetch('/api/reset_game', { method: 'POST' });
            hideCelebrationScreen();
            location.reload();
        };
        document.getElementById('btnCelebrationBugReport').onclick = () => {
            hideCelebrationScreen();
            openBugReport();
        };
    }

    // Update winner text
    const name = player_id === 0 ? "You" : `Player ${player_id}`;
    document.getElementById('celebrationMessage').textContent =
        `${name} won the game!`;

    // Display winning hand tiles
    const handDisplay = document.getElementById('winningHandDisplay');
    handDisplay.innerHTML = '';

    const melds = store.currentGameInfo.winning_revealed_sets;
    const hand = store.currentGameInfo.winning_hand;

    if (melds && melds.length > 0) {
        const meldsRow = document.createElement('div');
        meldsRow.className = 'winning-tiles-row';
        melds.forEach(meld => {
            const group = document.createElement('span');
            group.className = 'meld-group';
            meld.tiles.forEach(t => group.appendChild(createCelebrationTile(t)));
            meldsRow.appendChild(group);
        });
        handDisplay.appendChild(meldsRow);
    }

    if (hand && hand.length > 0) {
        const sorted = [...hand].sort((a, b) => a.localeCompare(b));
        const handRow = document.createElement('div');
        handRow.className = 'winning-tiles-row';
        sorted.forEach(t => handRow.appendChild(createCelebrationTile(t)));
        handDisplay.appendChild(handRow);
    }

    if ((!hand || hand.length === 0) && (!melds || melds.length === 0)) {
        handDisplay.innerHTML = '<p style="color:#666; font-size:0.9em;">Winning hand not available</p>';
    }

    elements.celebrationOverlay.style.display = 'flex';
}

export function hideCelebrationScreen() {
    if (elements.celebrationOverlay) {
        elements.celebrationOverlay.style.display = 'none';
    }
}
