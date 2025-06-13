import { elements, store, clearAllTimeouts } from './gameStore.js';

function sortTiles(tiles) {
    return [...tiles].sort((a, b) => {
        return a.unicode.localeCompare(b.unicode)
    });
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
            nextGameBtn.onclick = async () => {
                try {
                    // Advance dealer rotation - assume it was a draw (no winner)
                    const advanceResponse = await fetch('/api/advance_dealer', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ dealer_won: false })
                    });
                    
                    if (advanceResponse.ok) {
                        // Start new game
                        const newGameResponse = await fetch('/api/start_new_game', {
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
            };
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

function createTileElement(tile) {
    const tileEl = document.createElement('span');
    tileEl.textContent = `${tile.unicode}`;
    tileEl.style.border = "1px solid #ccc";
    tileEl.style.padding = "1px";
    tileEl.style.margin = "0px";
    tileEl.style.cursor = "pointer";

    // Count occurrences of this tile in the hand
    const tileCount = store.currentHandTiles.filter(t => t.suit === tile.suit && t.value === tile.value).length;

    if (tileCount === 4) {
        tileEl.classList.add('self-kongable'); // Add CSS class for styling
        tileEl.onclick = async () => {
            if (store.currentGameInfo.winner_found) return;
            // Hidden Kong can usually be declared on player's turn, often after drawing.
            // We assume it's the player's turn if this handler is active.
            // Add additional checks if isPlayerTurn is available and relevant here.

            if (confirm(`Declare a hidden Kong with ${tile.suit} ${tile.value}?`)) {
                const tileData = { suit: tile.suit, value: tile.value };
                try {
                    const response = await fetch('/api/player_declares_hidden_kong', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ tile_info: tileData })
                    });
                    const result = await response.json();
                    if (result && result.success) {
                        displayHand(result.hand);
                        displayRevealedSets(result.revealed_sets);
                        if (elements.playerConsoleEl) {
                            elements.playerConsoleEl.textContent = result.message;
                        }
                        // After successful Kong, player usually needs to discard.
                        // The backend should ideally dictate button states if a replacement tile was drawn.
                        if (elements.btnDiscardTile) elements.btnDiscardTile.disabled = false;
                        if (elements.btnDrawTile) elements.btnDrawTile.disabled = true;

                        if (result.drawn_tile && elements.playerConsoleEl) {
                            elements.playerConsoleEl.textContent += ` Replacement tile drawn: ${result.drawn_tile.unicode}`;
                        }

                    } else if (result && result.error) {
                        if (elements.playerConsoleEl) {
                            elements.playerConsoleEl.textContent = "Error declaring Hidden Kong: " + result.error;
                        }
                    } else {
                        if (elements.playerConsoleEl) {
                            elements.playerConsoleEl.textContent = "Failed to declare Hidden Kong. Unknown error.";
                        }
                    }
                } catch (error) {
                    console.error("EEL call failed for Hidden Kong:", error);
                    if (elements.playerConsoleEl) {
                        elements.playerConsoleEl.textContent = "An unexpected error occurred while declaring Hidden Kong.";
                    }
                }
            }
        };
    } else {
        // Default click handler for discarding
        tileEl.onclick = () => handleTileClick(tile, tileEl);
    }
    return tileEl;
}

function handleTileClick(tile, tileEl) {
    if (store.currentGameInfo.winner_found) return;    // Allow tile selection when it's our turn to discard (button is enabled)
    if (elements.btnDiscardTile && !elements.btnDiscardTile.disabled) {
        // Clear any active discard timeout when manually selecting a tile
        if (store.discardTimeoutId) {
            clearTimeout(store.discardTimeoutId);
            store.discardTimeoutId = null;
        }
        
        store.selectedTileForDiscard = tile;
        if (elements.selectedTileDisplayEl) {
            elements.selectedTileDisplayEl.textContent = `Selected: ${tile.unicode}`;
        }
        document.querySelectorAll('#player-hand span').forEach(el => {
            el.style.backgroundColor = 'transparent';
            // Ensure self-kongable tiles retain their border if not selected
            if (!el.classList.contains('self-kongable') || el === tileEl) {
                // If it is self-kongable and selected, lightblue is fine.
                // If not self-kongable, or self-kongable and selected, apply/remove background.
            }
        });
        tileEl.style.backgroundColor = 'lightblue'; // Highlight selected tile
        
        // Update console message to indicate manual selection
        if (elements.playerConsoleEl) {
            elements.playerConsoleEl.textContent = `Selected: ${tile.unicode}. Press 'D' or click Discard to proceed.`;
        }
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

export function displayRevealedSets(revealed_sets_data) {
    if (!elements.revealedSetsEl) return;

    if (!revealed_sets_data || revealed_sets_data.length === 0) {
        elements.revealedSetsEl.textContent = "";
        return;
    }

    let html = "";
    revealed_sets_data.forEach(meld => {
        const tilesString = meld.tiles.map(t => `${t.unicode}`).join(' ');
        html += `[${tilesString}]`;
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
    const discardArea = elements.discardArea;
    discardArea.innerHTML = '';
    // Add a flex container for each row
    const numTilesPerRow = 16;
    
    // Reverse the tiles array so newest tiles appear at top left
    const reversedTiles = [...store.discardedTiles].reverse();
    let currentRow;

    reversedTiles.forEach((tile, index) => {
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

        // If it's the latest discarded tile (first in reversed array), highlight it
        if (index === 0) {
            tileElement.style.border = '1px solid #ff6b6b';
            tileElement.style.boxShadow = '0 0 1px rgba(255,107,107,0.5)';
        }
        tileElement.textContent = tile.unicode;
        currentRow.appendChild(tileElement);
    });
}
