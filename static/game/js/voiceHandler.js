import { elements, store } from './gameStore.js';
import { parseTile } from './voiceParser.js';

function selectTile(tileChar) {
  if (!elements.btnDiscardTile || elements.btnDiscardTile.disabled) return;
  const tiles = document.querySelectorAll('#player-hand span');
  for (const el of tiles) {
    if (el.textContent === tileChar) {
      store.selectedTileForDiscard = tileChar;
      if (elements.selectedTileDisplayEl) {
        elements.selectedTileDisplayEl.textContent = `Selected: ${tileChar}`;
      }
      tiles.forEach(t => (t.style.backgroundColor = 'transparent'));
      el.style.backgroundColor = 'lightblue';
      return;
    }
  }
}

window.addEventListener('voice-command', e => {
  const text = e.detail.toLowerCase();

  if (text.includes('claim') || text.includes('kong') || text.includes('pung')) {
    if (elements.btnClaimYes && !elements.btnClaimYes.disabled) {
      elements.btnClaimYes.click();
    }
    return;
  }

  if (text.includes('win')) {
    if (elements.btnClaimYes && !elements.btnClaimYes.disabled &&
        (store.activeClaimType === 'WIN' || store.activeClaimType === 'SELF_DRAW_WIN')) {
      elements.btnClaimYes.click();
    }
    return;
  }

  if (text.startsWith('select')) {
    const tileName = text.replace(/^select/, '').trim();
    const tileChar = parseTile(tileName);
    if (tileChar) {
      selectTile(tileChar);
    }
  }
});

