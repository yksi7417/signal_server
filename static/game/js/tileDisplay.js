import { apiUrl } from './config.js';
import { elements, store, clearAllTimeouts } from './gameStore.js';

function sortTiles(tiles) {
    return [...tiles].sort((a, b) => a.localeCompare(b));
}

// Unicode → Pomax spritesheet tile ID mapping
// Spritesheet: 9 cols × 5 rows. col = id%9, row = id/9
const UNICODE_TO_TILE_ID = {};
// Winds: U+1F000-U+1F003 → East(27), South(28), West(29), North(30)
for (let i = 0; i <= 3; i++) UNICODE_TO_TILE_ID[0x1F000 + i] = 27 + i;
// Dragons: U+1F004=Red(33), U+1F005=Green(32), U+1F006=White(31)
UNICODE_TO_TILE_ID[0x1F004] = 33;
UNICODE_TO_TILE_ID[0x1F005] = 32;
UNICODE_TO_TILE_ID[0x1F006] = 31;
// Characters 1-9: U+1F007-U+1F00F → 9-17
for (let i = 0; i <= 8; i++) UNICODE_TO_TILE_ID[0x1F007 + i] = 9 + i;
// Bamboo 1-9: U+1F010-U+1F018 → 0-8
for (let i = 0; i <= 8; i++) UNICODE_TO_TILE_ID[0x1F010 + i] = i;
// Dots 1-9: U+1F019-U+1F021 → 18-26
for (let i = 0; i <= 8; i++) UNICODE_TO_TILE_ID[0x1F019 + i] = 18 + i;

function unicodeToTileId(tile) {
    if (!tile) return -1;
    const cp = tile.codePointAt(0);
    return UNICODE_TO_TILE_ID[cp] ?? -1;
}

function createTileImage(tile, sizeClass = 'tile-img-discard') {
    const tileId = unicodeToTileId(tile);
    const el = document.createElement('div');
    el.className = `tile-img ${sizeClass}`;
    if (tileId >= 0) {
        const col = tileId % 9;
        const row = Math.floor(tileId / 9);
        el.style.setProperty('--col', col);
        el.style.setProperty('--row', row);
    }
    return el;
}

function createTileBack() {
    const el = document.createElement('div');
    el.className = 'tile-back';
    return el;
}

export function displayHand(tiles) {
    if (!elements.playerHandEl) return;
    store.currentHandTiles = tiles || [];

    if (store.currentHandTiles.length === 0) {        
        elements.playerHandEl.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <p style="font-size: 18px; margin-bottom: 15px;">No tiles in hand.</p>
                <button id="next-game-btn" style="
                    padding: 12px 24px;
                    font-size: 16px;
                    font-weight: bold;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    margin-top: 10px;
                    transition: background-color 0.3s ease;
                " onmouseover="this.style.backgroundColor='#45a049'" 
                   onmouseout="this.style.backgroundColor='#4CAF50'">Continue to Next Game</button>
            </div>
        `;
        
        // Add click handler for the next game button
        const nextGameBtn = document.getElementById('next-game-btn');
        if (nextGameBtn) {
            nextGameBtn.addEventListener('click', async () => {
                try {
                    // Advance dealer rotation - assume it was a draw (no winner)
                    const advanceResponse = await fetch(apiUrl('/api/advance_dealer'), {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ dealer_won: false })
                    });
                    
                    if (advanceResponse.ok) {
                        // Start new game
                        const newGameResponse = await fetch(apiUrl('/api/start_new_game'), {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' }
                        });
                        
                        if (newGameResponse.ok) {
                            const gameInfo = await newGameResponse.json();
                            
                            // Update the display with new game info
                            displayHand(gameInfo.player_hand);
                            displayGameInfo(gameInfo);
                            
                            // Clear discard area
                            store.discardedTiles = [];
                            displayDiscardedTiles();
                              // Reset revealed sets
                            displayRevealedSets([]);
                            
                            // Clear selected tile
                            store.selectedTileForDiscard = null;
                            if (elements.selectedTileDisplayEl) {
                                elements.selectedTileDisplayEl.textContent = "Selected:";
                            }
                              // Update console message and auto-draw
                            if (elements.playerConsoleEl) {
                                elements.playerConsoleEl.textContent = "New game started! Auto-drawing tile...";
                            }
                            
                            // Reset game state flags
                            store.currentGameInfo.winner_found = false;
                            store.currentGameInfo.game_ended = false;
                            
                            // Auto-draw after a short delay to ensure UI is ready
                            setTimeout(async () => {
                                try {
                                    const { handleDrawTile } = await import('./gameActions.js');
                                    await handleDrawTile();
                                } catch (error) {
                                    console.error("Error during auto-draw:", error);
                                    if (elements.playerConsoleEl) {
                                        elements.playerConsoleEl.textContent = "Error auto-drawing. You may need to click Draw Tile manually.";
                                    }
                                    if (elements.btnDrawTile) elements.btnDrawTile.disabled = false;
                                    if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = true;
                                }
                            }, 200);
                            
                        } else {
                            console.error('Failed to start new game');
                            if (elements.playerConsoleEl) {
                                elements.playerConsoleEl.textContent = "Error starting new game. Please try again.";
                            }
                        }
                    } else {
                        console.error('Failed to advance dealer');
                        if (elements.playerConsoleEl) {
                            elements.playerConsoleEl.textContent = "Error advancing to next game. Please try again.";
                        }
                    }
                } catch (error) {
                    console.error('Error continuing to next game:', error);
                    if (elements.playerConsoleEl) {
                        elements.playerConsoleEl.textContent = "Error continuing to next game. Please try again.";
                    }
                }
            });
        }
        return;
    }

    const sortedTiles = sortTiles(store.currentHandTiles);
    store.currentHandTiles = sortedTiles;

    elements.playerHandEl.innerHTML = '';
    sortedTiles.forEach((tile, index) => {
        const tileEl = createTileElement(tile);
        elements.playerHandEl.appendChild(tileEl);
        if (index < sortedTiles.length - 1) {
            elements.playerHandEl.appendChild(document.createTextNode(''));
        }
    });
}

async function handleKongClick(tile, kongType) {
    if (store.currentGameInfo.winner_found) return;

    const label = kongType === 'hidden' ? 'hidden Kong' : 'add Kong (promote Pung)';
    const endpoint = kongType === 'hidden'
        ? '/api/player_declares_hidden_kong'
        : '/api/player_declares_add_kong';

    if (confirm(`Declare ${label} with ${tile}?`)) {
        try {
            const response = await fetch(apiUrl(endpoint), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tile_info: tile })
            });
            const result = await response.json();
            if (result && result.success) {
                store.addKongTiles = []; // Clear after kong
                displayHand(result.hand);
                displayRevealedSets(result.revealed_sets);
                if (elements.playerConsoleEl) {
                    elements.playerConsoleEl.textContent = result.message;
                }
                if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = false;
                if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;

                if (result.drawn_tile && elements.playerConsoleEl) {
                    elements.playerConsoleEl.textContent += ` Replacement tile drawn: ${result.drawn_tile}`;
                }
                if (result.winner_found) {
                    store.currentGameInfo.winner_found = true;
                    store.currentGameInfo.winning_player_id = result.winning_player_id;
                }
            } else if (result && result.error) {
                if (elements.playerConsoleEl) {
                    elements.playerConsoleEl.textContent = `Error declaring ${label}: ${result.error}`;
                }
            }
        } catch (error) {
            console.error(`Error declaring ${label}:`, error);
            if (elements.playerConsoleEl) {
                elements.playerConsoleEl.textContent = `Unexpected error declaring ${label}.`;
            }
        }
    }
}

function createTileElement(tile) {
    const tileEl = document.createElement('span');
    tileEl.dataset.tile = tile;
    const img = createTileImage(tile, 'tile-img-hand');
    tileEl.appendChild(img);

    // Count occurrences of this tile in the hand
    const tileCount = store.currentHandTiles.filter(t => t === tile).length;

    // Check if tile can be added to an exposed pung (add kong)
    const isAddKongable = store.addKongTiles && store.addKongTiles.includes(tile);

    if (tileCount === 4) {
        tileEl.classList.add('self-kongable');
        tileEl.addEventListener('click', () => handleKongClick(tile, 'hidden'));
    } else if (isAddKongable) {
        tileEl.classList.add('add-kongable');
        tileEl.addEventListener('click', () => handleKongClick(tile, 'add'));
    } else {
        // Default click handler for discarding
        tileEl.addEventListener('click', () => handleTileClick(tile, tileEl));
    }
    return tileEl;
}

function handleTileClick(tile, tileEl) {
    if (store.currentGameInfo.winner_found) return;
    if (elements.btnDiscardTile && !elements.btnDiscardTile.disabled) {
        const tileElements = document.querySelectorAll('#player-hand span');
        const index = Array.from(tileElements).indexOf(tileEl);
        selectTileByIndex(index);
    } else {
        if (elements.playerConsoleEl) {
            if (elements.btnDrawTile && !elements.btnDrawTile.disabled) {
                elements.playerConsoleEl.textContent = "Draw a tile first or declare a Kong if possible.";
            } else if (elements.btnDiscardTile && elements.btnDiscardTile.disabled) {
                elements.playerConsoleEl.textContent = "It's not your turn to discard or action pending.";
            }
        }
    }
}

export function selectTileByIndex(index) {
    const tileElements = document.querySelectorAll('#player-hand span');
    if (tileElements.length === 0) return;
    if (index < 0) index = 0;
    if (index >= tileElements.length) index = tileElements.length - 1;

    store.selectedTileIndex = index;
    store.selectedTileForDiscard = store.currentHandTiles[index];

    if (elements.selectedTileDisplayEl) {
        elements.selectedTileDisplayEl.textContent = `Selected: ${store.selectedTileForDiscard}`;
    }

    tileElements.forEach(el => el.classList.remove('tile-selected'));
    tileElements[index].classList.add('tile-selected');
}

export function displayRevealedSets(revealed_sets_data) {
    if (!elements.revealedSetsEl) return;

    if (!revealed_sets_data || revealed_sets_data.length === 0) {
        elements.revealedSetsEl.innerHTML = "";
        return;
    }

    elements.revealedSetsEl.innerHTML = '';
    revealed_sets_data.forEach(meld => {
        const group = document.createElement('span');
        group.className = 'meld-group';
        meld.tiles.forEach(t => {
            group.appendChild(createTileImage(t, 'tile-img-meld'));
        });
        elements.revealedSetsEl.appendChild(group);
    });
}

export function displayGameInfo(info) {
    if (!elements.gameInfoEl) return;
    if (!info) {
        elements.gameInfoEl.textContent = "";
        return;
    }

    elements.gameInfoEl.innerHTML = `
        Wind: ${info.game_wind || 'N/A'}<br>
    `;

    // Update remaining tiles count
    const remainingTilesEl = document.getElementById('remaining-tiles');
    if (remainingTilesEl && typeof info.remaining_tiles !== 'undefined') {
        remainingTilesEl.textContent = `Tiles: ${info.remaining_tiles}`;
    }

    if (info) {
        store.currentGameInfo = { ...store.currentGameInfo, ...info };
    }
}

export function displayDiscardedTiles() {
    // No-op: per-player discards are now rendered by displayPlayersInfo() from backend data
}

function renderPlayerDiscards(container, discards) {
    if (!container || !discards) return;
    container.innerHTML = '';
    discards.forEach((tile, index) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'discard-tile';
        if (index === discards.length - 1) wrapper.classList.add('latest');
        wrapper.appendChild(createTileImage(tile, 'tile-img-discard'));
        container.appendChild(wrapper);
    });
}

function renderPlayerMelds(container, sets) {
    if (!container || !sets) return;
    container.innerHTML = '';
    sets.forEach(meld => {
        const group = document.createElement('span');
        group.className = 'meld-group';
        meld.tiles.forEach(t => {
            group.appendChild(createTileImage(t, 'tile-img-meld'));
        });
        container.appendChild(group);
    });
}

const WIND_ORDER = { 'East': 0, 'South': 1, 'West': 2, 'North': 3 };
const WIND_ABBREV = { 'East': 'E', 'South': 'S', 'West': 'W', 'North': 'N' };

export function displayPlayersInfo(playersInfo, currentPlayerId) {
    if (!playersInfo) return;
    store.playersInfo = playersInfo;

    playersInfo.forEach((p, idx) => {
        // Label with wind abbreviation prefix
        const label = elements.playerLabels[idx];
        if (label) {
            const name = idx === 0 ? "You" : `P${idx}`;
            const windAbbr = WIND_ABBREV[p.wind] || '--';
            label.textContent = `${windAbbr} ${name}`;
        }

        // Turn indicator
        const area = elements.playerAreas[idx];
        if (area) area.classList.toggle('active-turn', p.player_id === currentPlayerId);

        // Discards for ALL players (from backend data)
        const dc = elements.playerDiscards[idx];
        if (dc) renderPlayerDiscards(dc, p.discards);

        // Melds (P0 handled by existing displayRevealedSets)
        if (idx !== 0) {
            const mc = elements.playerMelds[idx];
            if (mc) renderPlayerMelds(mc, p.revealed_sets);
        }

        // Hand tiles for opponents (face-down tile backs)
        if (idx !== 0) {
            const hc = elements.playerHandCounts[idx];
            if (hc) {
                hc.innerHTML = '';
                for (let i = 0; i < p.hand_count; i++) {
                    hc.appendChild(createTileBack());
                }
            }
        }
    });

    // Update center discard labels with wind abbreviations
    playersInfo.forEach(p => {
        const discardLabel = document.getElementById(`discard-label-${p.player_id}`);
        if (discardLabel) {
            const windAbbr = WIND_ABBREV[p.wind] || '--';
            const name = p.player_id === 0 ? 'You' : `P${p.player_id}`;
            discardLabel.textContent = `${windAbbr} ${name}`;
        }
    });

    // Reorder center discard rows by wind sequence (E -> S -> W -> N)
    const centerDiscards = document.getElementById('center-discards');
    if (centerDiscards && playersInfo.length > 0) {
        const rows = Array.from(centerDiscards.querySelectorAll('.center-discard-row'));
        if (rows.length > 0) {
            // Build map: player_id -> wind order
            const playerWindOrder = {};
            playersInfo.forEach(p => {
                playerWindOrder[p.player_id] = WIND_ORDER[p.wind] ?? 99;
            });
            // Sort rows by their player's wind order
            rows.sort((a, b) => {
                const aId = parseInt(a.dataset.playerId ?? '99', 10);
                const bId = parseInt(b.dataset.playerId ?? '99', 10);
                return (playerWindOrder[aId] ?? 99) - (playerWindOrder[bId] ?? 99);
            });
            rows.forEach(row => centerDiscards.appendChild(row));
        }
    }
}
