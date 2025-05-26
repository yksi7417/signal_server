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
    tileEl.style.padding = "1px";
    tileEl.style.margin = "0px";
    tileEl.style.cursor = "pointer";
    tileEl.onclick = () => handleTileClick(tile, tileEl);
    return tileEl;
}

function handleTileClick(tile, tileEl) {
    if (store.currentGameInfo.winner_found) return;
    
    if (store.currentHandTiles.length === store.INIT_HAND_SIZE + 1 && !elements.btnDiscardTile.disabled) {
        store.selectedTileForDiscard = tile;
        if (elements.selectedTileDisplayEl) {
            elements.selectedTileDisplayEl.textContent = `Selected Tile: ${tile.unicode}`;
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

export function displayDiscardedTiles() {
    const discardArea = elements.discardArea;
    discardArea.innerHTML = '';
      // Add a flex container for each row
    const numTilesPerRow = 10;
    let currentRow;
    
    store.discardedTiles.forEach((tile, index) => {
        // Create a new row every 10 tiles
        if (index % numTilesPerRow === 0) {
            currentRow = document.createElement('div');
            currentRow.style.cssText = `
                display: flex;
                justify-content: center;
                margin-bottom: 1px;
            `;
            discardArea.appendChild(currentRow);
        }
        
        const tileElement = document.createElement('div');
        tileElement.className = 'mahjong-tile';
        tileElement.style.cssText = `
            width: 45px;
            height: 63px;
            background-color: white;
            border: 2px solid #999;
            border-radius: 3px;
            margin: 1px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 42px;
            line-height: 1;
            box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        `;
        
        // If it's the latest discarded tile, highlight it
        if (index === store.discardedTiles.length - 1) {
            tileElement.style.border = '1px solid #ff6b6b';
            tileElement.style.boxShadow = '0 0 1px rgba(255,107,107,0.5)';
        }
          tileElement.textContent = tile.unicode;
        currentRow.appendChild(tileElement);
    });
}
