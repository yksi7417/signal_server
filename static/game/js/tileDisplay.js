import { store, elements } from './gameStore.js';

export function displayHand(tiles) {
    if (!elements.playerHandEl) return;
    store.currentHandTiles = tiles || [];
    
    if (store.currentHandTiles.length === 0) {
        elements.playerHandEl.textContent = "No tiles in hand.";
        return;
    }
    
    elements.playerHandEl.innerHTML = '';
    store.currentHandTiles.forEach((tile, index) => {
        const tileEl = createTileElement(tile);
        elements.playerHandEl.appendChild(tileEl);
        if (index < store.currentHandTiles.length - 1) {
            elements.playerHandEl.appendChild(document.createTextNode(''));
        }
    });
}

function createTileElement(tile) {
    const tileEl = document.createElement('span');
    tileEl.textContent = `${tile.unicode}`;
    tileEl.style.border = "1px solid #ccc";
    tileEl.style.padding = "5px";
    tileEl.style.margin = "2px";
    tileEl.style.cursor = "pointer";
    tileEl.onclick = () => handleTileClick(tile, tileEl);
    return tileEl;
}

function handleTileClick(tile, tileEl) {
    if (store.currentGameInfo.winner_found) return;
    
    if (store.currentHandTiles.length === store.INIT_HAND_SIZE + 1 && !elements.btnDiscardTile.disabled) {
        store.selectedTileForDiscard = tile;
        if (elements.selectedTileDisplayEl) {
            elements.selectedTileDisplayEl.textContent = `Selected Tile: ${tile.suit} ${tile.value}`;
        }
        document.querySelectorAll('#player-hand span').forEach(el => el.style.backgroundColor = 'transparent');
        tileEl.style.backgroundColor = 'lightblue';
    } else {
        if (elements.playerConsoleEl && !elements.btnDiscardTile.disabled) {
            elements.playerConsoleEl.textContent = "Draw a tile first or ensure it's your turn to discard.";
        } else if (elements.playerConsoleEl && elements.btnDiscardTile.disabled && !elements.btnDrawTile.disabled) {
            elements.playerConsoleEl.textContent = "Draw a tile first.";
        }
    }
}

export function displayRevealedSets(revealed_sets_data) {
    if (!elements.revealedSetsEl) return;
    
    if (!revealed_sets_data || revealed_sets_data.length === 0) {
        elements.revealedSetsEl.textContent = "Revealed Sets: None";
        return;
    }
    
    let html = "Revealed Sets: ";
    revealed_sets_data.forEach(meld => {
        const tilesString = meld.tiles.map(t => `${t.suit} ${t.value}`).join(', ');
        html += `${meld.type} (${tilesString})`;
    });
    elements.revealedSetsEl.innerHTML = html;
}

export function displayGameInfo(info) {
    if (!elements.gameInfoEl) return;
    if (!info) {
        elements.gameInfoEl.textContent = "";
        return;
    }
    
    elements.gameInfoEl.innerHTML = `
        Game Wind: ${info.game_wind || 'N/A'}<br>
        Current Player ID: ${info.current_player_id !== undefined ? info.current_player_id : 'N/A'}
    `;
    if (info) {
        store.currentGameInfo = { ...store.currentGameInfo, ...info };
    }
}
