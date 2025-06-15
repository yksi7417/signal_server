import { elements, store } from './gameStore.js';
import { handleClaimYes } from './claimsHandler.js';

// Unicode mapping for tiles based on suit and value
const tileUnicode = {
  Characters: {
    '1': '\u{1F007}', '2': '\u{1F008}', '3': '\u{1F009}', '4': '\u{1F00A}',
    '5': '\u{1F00B}', '6': '\u{1F00C}', '7': '\u{1F00D}', '8': '\u{1F00E}',
    '9': '\u{1F00F}'
  },
  Bamboo: {
    '1': '\u{1F010}', '2': '\u{1F011}', '3': '\u{1F012}', '4': '\u{1F013}',
    '5': '\u{1F014}', '6': '\u{1F015}', '7': '\u{1F016}', '8': '\u{1F017}',
    '9': '\u{1F018}'
  },
  Dots: {
    '1': '\u{1F019}', '2': '\u{1F01A}', '3': '\u{1F01B}', '4': '\u{1F01C}',
    '5': '\u{1F01D}', '6': '\u{1F01E}', '7': '\u{1F01F}', '8': '\u{1F020}',
    '9': '\u{1F021}'
  },
  Winds: {
    East: '\u{1F000}', South: '\u{1F001}', West: '\u{1F002}', North: '\u{1F003}'
  },
  Dragons: {
    Red: '\u{1F004}', Green: '\u{1F005}', White: '\u{1F006}'
  },
  Flowers: {
    Plum: '\u{1F022}', Orchid: '\u{1F023}', Chrysanthemum: '\u{1F024}', Bamboo: '\u{1F025}'
  },
  Seasons: {
    Spring: '\u{1F026}', Summer: '\u{1F027}', Autumn: '\u{1F028}', Winter: '\u{1F029}'
  }
};

const wordToNumber = {
  one: '1', two: '2', three: '3', four: '4', five: '5',
  six: '6', seven: '7', eight: '8', nine: '9'
};

const suitAliases = {
  bamboo: 'Bamboo', bam: 'Bamboo',
  dot: 'Dots', dots: 'Dots', circle: 'Dots', circles: 'Dots',
  character: 'Characters', characters: 'Characters', crack: 'Characters',
  wind: 'Winds', winds: 'Winds',
  dragon: 'Dragons', dragons: 'Dragons',
  flower: 'Flowers', flowers: 'Flowers',
  season: 'Seasons', seasons: 'Seasons'
};

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function parseTile(text) {
  const lower = text.toLowerCase();

  // Dragons
  for (const color of ['red', 'green', 'white']) {
    if (lower.includes(color) && lower.includes('dragon')) {
      return tileUnicode.Dragons[capitalize(color)];
    }
  }

  // Winds
  for (const dir of ['east', 'south', 'west', 'north']) {
    if (lower.includes(dir) && lower.includes('wind')) {
      return tileUnicode.Winds[capitalize(dir)];
    }
  }

  // Flowers
  for (const f of ['plum', 'orchid', 'chrysanthemum', 'bamboo']) {
    if (lower.includes(f) && (lower.includes('flower') || lower.includes('flowers'))) {
      return tileUnicode.Flowers[capitalize(f)];
    }
  }

  // Seasons
  for (const s of ['spring', 'summer', 'autumn', 'winter']) {
    if (lower.includes(s) && (lower.includes('season') || lower.includes('seasons'))) {
      return tileUnicode.Seasons[capitalize(s)];
    }
  }

  // Numeric suits
  const tokens = lower.split(/\s+/);
  let value = null;
  let suit = null;
  for (const t of tokens) {
    if (wordToNumber[t]) value = wordToNumber[t];
    else if (/^[1-9]$/.test(t)) value = t;
    if (suitAliases[t]) suit = suitAliases[t];
  }

  if (value && suit && tileUnicode[suit] && tileUnicode[suit][value]) {
    return tileUnicode[suit][value];
  }

  return null;
}

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

