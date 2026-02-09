import { elements } from './gameStore.js';
import { openBugReport } from './bugReport.js';

export function showCelebrationScreen(player_id) {
    // Create celebration overlay if it doesn't exist
    if (!elements.celebrationOverlay) {
        const overlay = document.createElement('div');
        overlay.id = 'celebrationOverlay';
        overlay.style.display = 'none';
        overlay.innerHTML = `
            <div class="celebration-content">
                <h1>🎉 WINNER! 🎉</h1>
                <h2 id="celebrationMessage"></h2>
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

    // Update the winner text every time (not just on creation)
    document.getElementById('celebrationMessage').textContent =
        `Player ${player_id} has won the game!`;

    elements.celebrationOverlay.style.display = 'flex';
}

export function hideCelebrationScreen() {
    if (elements.celebrationOverlay) {
        elements.celebrationOverlay.style.display = 'none';
    }
}
