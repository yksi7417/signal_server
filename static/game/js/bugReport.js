/**
 * Bug Report UI with voice dictation.
 *
 * Opens a modal where the user can type or dictate (via Web Speech API)
 * what went wrong, edit the text, and submit to POST /api/report_bug.
 */

let modal = null;
let textarea = null;
let micBtn = null;
let submitBtn = null;
let cancelBtn = null;
let statusEl = null;
let resultArea = null;

let recognition = null;
let isListening = false;

// ── Build the modal DOM (once) ──────────────────────────────────────

function ensureModal() {
  if (modal) return;

  modal = document.createElement('div');
  modal.id = 'bug-report-modal';
  modal.innerHTML = `
    <div class="br-backdrop"></div>
    <div class="br-dialog">
      <h3>Report a Bug</h3>
      <p class="br-hint">Describe what went wrong. You can type or tap the mic to dictate.</p>
      <div class="br-input-row">
        <textarea id="br-description" rows="5"
          placeholder="e.g. I clicked Pung but nothing happened..."></textarea>
        <button id="br-mic" title="Toggle voice input">&#x1F3A4;</button>
      </div>
      <div id="br-status" class="br-status"></div>
      <div id="br-result" class="br-result" style="display:none;"></div>
      <div class="br-actions">
        <button id="br-submit">Submit Bug Report</button>
        <button id="br-cancel">Cancel</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);

  textarea   = document.getElementById('br-description');
  micBtn     = document.getElementById('br-mic');
  submitBtn  = document.getElementById('br-submit');
  cancelBtn  = document.getElementById('br-cancel');
  statusEl   = document.getElementById('br-status');
  resultArea = document.getElementById('br-result');

  micBtn.addEventListener('click', toggleVoice);
  submitBtn.addEventListener('click', submitReport);
  cancelBtn.addEventListener('click', closeBugReport);

  // Close on backdrop click
  modal.querySelector('.br-backdrop').addEventListener('click', closeBugReport);
}

// ── Speech recognition ──────────────────────────────────────────────

function initSpeech() {
  if (recognition) return true;

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return false;

  recognition = new SR();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = navigator.language || 'en-US';

  recognition.onresult = (event) => {
    // Accumulate final results into the textarea
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        const text = event.results[i][0].transcript;
        textarea.value += text;
      }
    }
    // Show interim text in status
    const last = event.results[event.results.length - 1];
    if (!last.isFinal) {
      statusEl.textContent = last[0].transcript;
      statusEl.style.color = '#666';
    } else {
      statusEl.textContent = '';
    }
  };

  recognition.onerror = (event) => {
    statusEl.textContent = 'Voice error: ' + event.error;
    statusEl.style.color = '#c00';
    stopListening();
  };

  recognition.onend = () => {
    if (isListening) {
      // Auto-restart if user hasn't toggled off
      try { recognition.start(); } catch (_) { /* ignore */ }
    }
  };

  return true;
}

function toggleVoice() {
  if (isListening) {
    stopListening();
  } else {
    startListening();
  }
}

function startListening() {
  if (!initSpeech()) {
    statusEl.textContent = 'Voice input not supported in this browser.';
    statusEl.style.color = '#c00';
    return;
  }
  try {
    recognition.start();
    isListening = true;
    micBtn.classList.add('br-mic-active');
    statusEl.textContent = 'Listening...';
    statusEl.style.color = '#2E7D32';
  } catch (e) {
    statusEl.textContent = 'Could not start voice: ' + e.message;
    statusEl.style.color = '#c00';
  }
}

function stopListening() {
  isListening = false;
  if (recognition) {
    try { recognition.stop(); } catch (_) { /* ignore */ }
  }
  micBtn.classList.remove('br-mic-active');
  statusEl.textContent = '';
}

// ── Submit / Close ──────────────────────────────────────────────────

async function submitReport() {
  const description = textarea.value.trim();
  if (!description) {
    statusEl.textContent = 'Please describe the bug first.';
    statusEl.style.color = '#c00';
    return;
  }

  stopListening();
  submitBtn.disabled = true;
  statusEl.textContent = 'Submitting...';
  statusEl.style.color = '#666';

  try {
    const resp = await fetch('/api/report_bug', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    const data = await resp.json();

    if (data.success) {
      resultArea.style.display = 'block';

      if (data.auto_created) {
        // Issue was automatically created
        resultArea.innerHTML =
          '<b>✅ Bug reported & GitHub issue created!</b><br>' +
          'Bug ID: <code>' + data.bug_id + '</code><br>' +
          'GitHub Issue: <a href="' + data.issue_url +
          '" target="_blank" rel="noopener">#' + data.issue_number + '</a><br>' +
          '<details><summary>View report markdown</summary>' +
          '<pre>' + escapeHtml(data.markdown) + '</pre></details>';
      } else {
        // Manual issue creation needed
        const noTokenMsg = !data.auto_created && data.issue_url.includes('/issues/new')
          ? '<br><small>💡 Tip: Set GITHUB_TOKEN environment variable for automatic issue creation</small>'
          : '';
        resultArea.innerHTML =
          '<b>Bug reported!</b> ID: <code>' + data.bug_id + '</code><br>' +
          '<a href="' + data.issue_url +
          '" target="_blank" rel="noopener">Create GitHub Issue Manually</a>' +
          noTokenMsg +
          '<details><summary>Preview markdown</summary>' +
          '<pre>' + escapeHtml(data.markdown) + '</pre></details>';
      }

      statusEl.textContent = '';
      submitBtn.textContent = 'Submitted';
    } else {
      statusEl.textContent = 'Error: ' + (data.error || 'Unknown error');
      statusEl.style.color = '#c00';
      submitBtn.disabled = false;
    }
  } catch (e) {
    statusEl.textContent = 'Network error: ' + e.message;
    statusEl.style.color = '#c00';
    submitBtn.disabled = false;
  }
}

function escapeHtml(s) {
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

// ── Public API ──────────────────────────────────────────────────────

export function openBugReport() {
  ensureModal();
  // Reset state
  textarea.value = '';
  statusEl.textContent = '';
  resultArea.style.display = 'none';
  resultArea.innerHTML = '';
  submitBtn.disabled = false;
  submitBtn.textContent = 'Submit Bug Report';
  modal.style.display = 'block';
  textarea.focus();
}

export function closeBugReport() {
  stopListening();
  if (modal) modal.style.display = 'none';
}
