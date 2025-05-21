// cache DOM nodes
const btnDraw  = document.getElementById('draw');
const btnReset = document.getElementById('reset');
const resultEl = document.getElementById('result');
const histEl   = document.getElementById('hist-list');

// call Python draw_tile(), then display its return value
btnDraw.onclick = async () => {
  const tile = await eel.draw_tile()();
  resultEl.textContent = tile;
};

// call Python reset_game()
btnReset.onclick = async () => {
  await eel.reset_game()();
  resultEl.textContent = '🤷';
};

// expose a JS function so Python can push updates to us
eel.expose(update_history);
function update_history(hist) {
  histEl.textContent = hist.join(' ');
}

// on startup, fetch current history (empty) so UI syncs
(async()=>{
  const initial = await eel.reset_game()();
  // history callback will fire, so no further action needed here
})();
