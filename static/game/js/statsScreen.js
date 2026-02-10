// Stats and Leaderboard overlay
import { store } from './gameStore.js';
import { apiFetch } from './auth.js';

let statsOverlay = null;

function ensureOverlay() {
    if (statsOverlay) return;
    statsOverlay = document.createElement('div');
    statsOverlay.id = 'statsOverlay';
    statsOverlay.style.display = 'none';
    statsOverlay.innerHTML = `
        <div class="stats-content">
            <h1>Leaderboard</h1>
            <div id="leaderboardTable"></div>
            <h2 id="userStatsHeader" style="display:none;">Your Stats</h2>
            <div id="userStatsDisplay"></div>
            <h2 id="matchHistoryHeader" style="display:none;">Recent Matches</h2>
            <div id="matchHistoryList"></div>
            <button id="btnCloseStats">Close</button>
        </div>
    `;
    document.body.appendChild(statsOverlay);
    document.getElementById('btnCloseStats').addEventListener('click', hideStats);
}

export async function showStats() {
    ensureOverlay();

    // Fetch leaderboard
    try {
        const resp = await apiFetch('/api/leaderboard');
        const data = await resp.json();
        renderLeaderboard(data.leaderboard || []);
    } catch (e) {
        console.warn('Failed to load leaderboard:', e);
        renderLeaderboard([]);
    }

    // Fetch user stats if logged in
    if (store.currentUser) {
        try {
            const resp = await apiFetch('/api/user/profile');
            const data = await resp.json();
            if (data.success) {
                renderUserStats(data.stats);
                document.getElementById('userStatsHeader').style.display = '';
            }
        } catch (e) { /* guest mode */ }

        try {
            const resp = await apiFetch('/api/user/history');
            const data = await resp.json();
            if (data.success) {
                renderMatchHistory(data.history || []);
                document.getElementById('matchHistoryHeader').style.display = '';
            }
        } catch (e) { /* ignore */ }
    }

    statsOverlay.style.display = 'flex';
}

export function hideStats() {
    if (statsOverlay) statsOverlay.style.display = 'none';
}

function renderLeaderboard(entries) {
    const container = document.getElementById('leaderboardTable');
    if (!entries.length) {
        container.innerHTML = '<p>No games played yet.</p>';
        return;
    }
    let html = '<table class="leaderboard"><thead><tr><th>#</th><th>Player</th><th>Wins</th><th>Played</th><th>Best Faan</th></tr></thead><tbody>';
    entries.forEach((e, i) => {
        const winRate = e.games_played > 0 ? Math.round((e.games_won / e.games_played) * 100) : 0;
        html += `<tr><td>${i + 1}</td><td>${escapeHtml(e.display_name)}</td><td>${e.games_won}</td><td>${e.games_played}</td><td>${e.highest_faan}</td></tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

function renderUserStats(stats) {
    const container = document.getElementById('userStatsDisplay');
    if (!stats) {
        container.innerHTML = '';
        return;
    }
    const winRate = stats.games_played > 0 ? Math.round((stats.games_won / stats.games_played) * 100) : 0;
    container.innerHTML = `
        <div class="user-stats-grid">
            <div class="stat-box"><span class="stat-value">${stats.games_played}</span><span class="stat-label">Games</span></div>
            <div class="stat-box"><span class="stat-value">${stats.games_won}</span><span class="stat-label">Wins</span></div>
            <div class="stat-box"><span class="stat-value">${winRate}%</span><span class="stat-label">Win Rate</span></div>
            <div class="stat-box"><span class="stat-value">${stats.highest_faan}</span><span class="stat-label">Best Faan</span></div>
        </div>
    `;
}

function renderMatchHistory(history) {
    const container = document.getElementById('matchHistoryList');
    if (!history.length) {
        container.innerHTML = '<p>No matches yet.</p>';
        return;
    }
    let html = '<ul class="match-history">';
    history.forEach(m => {
        const cls = m.result === 'win' ? 'match-win' : m.result === 'loss' ? 'match-loss' : 'match-draw';
        const faan = m.faan_scored > 0 ? ` (${m.faan_scored} faan)` : '';
        html += `<li class="${cls}">${m.result.toUpperCase()}${faan} <span class="match-date">${m.played_at || ''}</span></li>`;
    });
    html += '</ul>';
    container.innerHTML = html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
