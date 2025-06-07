import { elements } from './gameStore.js';

export function showCelebrationScreen(player_id) {
    // Create celebration overlay if it doesn't exist
    if (!elements.celebrationOverlay) {
        const overlay = document.createElement('div');
        overlay.id = 'celebrationOverlay';
        overlay.style.display = 'none';
        overlay.innerHTML = `
            <div class="celebration-content">
                <h1>🎉 WINNER! 🎉</h1>
                <h2>Player ${player_id} has won the game!</h2>
                <button id="btnNewGame">Start New Game</button>
            </div>
        `;
        document.body.appendChild(overlay);
        elements.celebrationOverlay = overlay;
        // Add event listener to new game button
        const btnNewGame = document.getElementById('btnNewGame');
        btnNewGame.onclick = async () => {
            await fetch('/api/reset_game', { method: 'POST' });
            hideCelebrationScreen();
            location.reload(); // Refresh the page to start a new game
        };
    }

    // Show the celebration overlay
    elements.celebrationOverlay.style.display = 'flex';
}

export function hideCelebrationScreen() {
    if (elements.celebrationOverlay) {
        elements.celebrationOverlay.style.display = 'none';
    }
}
