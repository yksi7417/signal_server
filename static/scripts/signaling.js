const peers = {};
const pendingCandidates = {};
const peerJoinTimes = {};
let myId = localStorage.getItem("clientId") || "client-" + Math.floor(Math.random() * 10000);
localStorage.setItem("clientId", myId);
let localStream;
let ws;
let wsReady = false;
let isMuted = false;
let connected = false;


const peerList = document.getElementById("peerList");
const dingSound = document.getElementById("ding");

function updatePeerListUI() {
  peerList.innerHTML = "";

  // Add self first
  const li = document.createElement("li");
  li.className = `peer-entry self ${isMuted ? "muted" : "unmuted"}`;
  li.innerHTML = `
    <div class="mic-indicator" id="mic-${myId}"></div>
    <strong>${myId}</strong>
    <span>🕒 ${new Date().toLocaleTimeString()}</span>
    <span id="latency-${myId}">⏱️ --</span>
    <button onclick="toggleMuteSelf()">${isMuted ? "🔈" : "🔇"}</button>
    <input type="range" min="0" max="1" step="0.01" value="1" onchange="setVolume('${myId}', this.value)">
    <em>(you)</em>
  `;
  peerList.appendChild(li);

  // Add remote peers
  for (const [id, pc] of Object.entries(peers)) {
    const peerLi = document.createElement("li");
    const audio = document.getElementById(`audio-${id}`);
    const isPeerMuted = audio?.muted;

    peerLi.className = `peer-entry ${isPeerMuted ? "muted" : "unmuted"}`;
    peerLi.innerHTML = `
      <div class="mic-indicator" id="mic-${id}"></div>
      <strong>${id}</strong>
      <span>🕒 ${peerJoinTimes[id]?.toLocaleTimeString() || ""}</span>
      <span id="latency-${id}">⏱️ --</span>
      <button onclick="mutePeer('${id}')">🔇</button>
      <input type="range" min="0" max="1" step="0.01" value="1" onchange="setVolume('${id}', this.value)">
    `;
    peerList.appendChild(peerLi);
  }
}

async function handleStartOrEnd() {
  if (!connected) {
    startBtn.disabled = true;
    startBtn.textContent = "🔄 Connecting...";
    await new Promise(r => setTimeout(r));
    await start();
    startBtn.disabled = false;
    startBtn.textContent = "End Call";
    await new Promise(r => setTimeout(r));
    connected = true;
  } else {
    // End call
    if (ws && ws.readyState === WebSocket.OPEN) {
      safeSend({ type: "peer-disconnect", id: myId });
      ws.close();
    }
    Object.values(peers).forEach(pc => pc.close());
    Object.keys(peers).forEach(id => delete peers[id]);
    updatePeerListUI();
    if (localStream) {
      localStream.getTracks().forEach(t => t.stop());
    }
    startBtn.textContent = "Start Call";
    connected = false;
  }
}

function toggleMuteSelf() {
  const track = localStream.getAudioTracks()[0];
  if (track) {
    track.enabled = !track.enabled;
    isMuted = !track.enabled;
    updatePeerListUI();
  }
}

function safeSend(payload) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(payload));
  }
}

async function flushPendingCandidates(peerId, pc) {
  if (pendingCandidates[peerId]) {
    for (const c of pendingCandidates[peerId]) {
      await pc.addIceCandidate(new RTCIceCandidate(c));
    }
    delete pendingCandidates[peerId];
  }
}

function mutePeer(id) {
  const audio = document.getElementById(`audio-${id}`);
  if (audio) audio.muted = !audio.muted;
  updatePeerListUI();
}

function setVolume(id, level) {
  const audio = document.getElementById(`audio-${id}`);
  if (audio) audio.volume = level;
}

function monitorMicActivity(stream) {
  const ctx = new AudioContext();
  const analyser = ctx.createAnalyser();
  const mic = ctx.createMediaStreamSource(stream);
  mic.connect(analyser);
  const data = new Uint8Array(analyser.frequencyBinCount);

  function detect() {
    analyser.getByteFrequencyData(data);
    const vol = data.reduce((a, b) => a + b, 0) / data.length;
    const el = document.getElementById(`mic-${myId}`);
    if (el) el.classList.toggle("active", vol > 10);
    requestAnimationFrame(detect);
  }
  detect();
}

function monitorRemoteMicActivity(peerId, stream) {
  const ctx = new AudioContext();
  const analyser = ctx.createAnalyser();
  const source = ctx.createMediaStreamSource(stream);
  source.connect(analyser);
  const data = new Uint8Array(analyser.frequencyBinCount);

  function detect() {
    analyser.getByteFrequencyData(data);
    const vol = data.reduce((a, b) => a + b, 0) / data.length;
    const el = document.getElementById(`mic-${peerId}`);
    if (el) el.classList.toggle("active", vol > 10);
    requestAnimationFrame(detect);
  }
  detect();
}

function trackStats(peerId, pc) {
  setInterval(async () => {
    const stats = await pc.getStats();
    for (const report of stats.values()) {
      if (report.type === "candidate-pair" && report.currentRoundTripTime) {
        const el = document.getElementById(`latency-${peerId}`);
        if (el) el.textContent = `⏱️ ${Math.round(report.currentRoundTripTime * 1000)}ms`;
      }
    }
  }, 2000);
}

async function createPeerConnection(peerId, initiator = true) {
  if (peers[peerId]) return peers[peerId];

  const pc = new RTCPeerConnection({ iceServers: [{ urls: "stun:stun.l.google.com:19302" }] });
  pendingCandidates[peerId] = [];
  peerJoinTimes[peerId] = new Date();

  pc.onicecandidate = ({ candidate }) => {
    if (candidate) safeSend({ type: "candidate", candidate, from: myId, to: peerId });
  };

  pc.ontrack = ({ streams }) => {
    const stream = streams[0];
    const audio = new Audio();
    audio.srcObject = stream;
    audio.autoplay = true;
    audio.id = `audio-${peerId}`;
    document.body.appendChild(audio);
    monitorRemoteMicActivity(peerId, stream);
    updatePeerListUI();
  };

  localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));
  peers[peerId] = pc;

  trackStats(peerId, pc);
  updatePeerListUI();

  if (initiator) {
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    safeSend({ ...offer, from: myId, to: peerId });
  }

  return pc;
}

async function start() {
  const nameInput = document.getElementById("clientIdInput");
  if (nameInput && nameInput.value.trim()) {
    const newId = nameInput.value.trim();
    if (newId && newId !== myId) {
      // Disconnect current identity
      if (wsReady) {
        safeSend({ type: "peer-disconnect", id: myId });
      }
      myId = newId;
      localStorage.setItem("clientId", myId);
      if (wsReady) {
        safeSend({ type: "hello", id: myId });
      }
      updatePeerListUI();
    }
    myId = newId;
    localStorage.setItem("clientId", myId);
    if (wsReady) {
      safeSend({ type: "hello", id: myId });
    }
    updatePeerListUI();
    }
    localStorage.setItem("clientId", myId);
  }

  localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  monitorMicActivity(localStream);
  updatePeerListUI();

  ws = new WebSocket(window.APP_CONFIG.wsUrl);

  ws.onopen = () => {
    wsReady = true;
    safeSend({ type: "hello", id: myId });
  };

  ws.onmessage = async ({ data }) => {
    const msg = JSON.parse(data);
    const from = msg.from;

    if (msg.type === "peer-list") {
      for (const peerId of msg.peers) {
        const initiator = myId < peerId;
        await createPeerConnection(peerId, initiator);
      }
    } else if (msg.type === "new-peer") {
      const peerId = msg.id;
      if (!peers[peerId]) {
        const initiator = myId < peerId;
        await createPeerConnection(peerId, initiator);
        dingSound.play();
        updatePeerListUI();
      }
    } else if (msg.type === "peer-disconnect") {
      if (peers[msg.id]) {
        peers[msg.id].close();
        delete peers[msg.id];
        updatePeerListUI();
      }
    } else if (msg.type === "offer") {
      const pc = peers[from] || await createPeerConnection(from, false);
      await pc.setRemoteDescription(new RTCSessionDescription(msg));
      await flushPendingCandidates(from, pc);
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      safeSend({ ...answer, from: myId, to: from });
    } else if (msg.type === "answer") {
      const pc = peers[from];
      if (pc && pc.signalingState === "have-local-offer") {
        await pc.setRemoteDescription(new RTCSessionDescription(msg));
        await flushPendingCandidates(from, pc);
      }
    } else if (msg.type === "candidate") {
      const pc = peers[from];
      if (pc && pc.remoteDescription && pc.remoteDescription.type) {
        await pc.addIceCandidate(new RTCIceCandidate(msg.candidate));
      } else {
        if (!pendingCandidates[from]) pendingCandidates[from] = [];
        pendingCandidates[from].push(msg.candidate);
      }
    }
  };

  ws.onclose = () => {
    console.warn("WebSocket closed, refreshing in 20 seconds...");
    const banner = document.createElement("div");
    banner.id = "reconnect-banner";
    banner.textContent = "🔌 Disconnected. Reconnecting in 20 seconds...";
    banner.style.position = "fixed";
    banner.style.bottom = "10px";
    banner.style.left = "50%";
    banner.style.transform = "translateX(-50%)";
    banner.style.background = "#ffcccc";
    banner.style.color = "#333";
    banner.style.padding = "0.5rem 1rem";
    banner.style.borderRadius = "5px";
    banner.style.boxShadow = "0 0 6px rgba(0,0,0,0.2)";
    banner.style.zIndex = "1000";
    banner.style.fontWeight = "bold";
    document.body.appendChild(banner);

    let countdown = 20;
    const interval = setInterval(() => {
      countdown--;
      banner.textContent = `🔌 Disconnected. Reconnecting in ${countdown} seconds...`;
      if (countdown <= 0) clearInterval(interval);
    }, 1000);

    setTimeout(() => location.reload(), 20000);
  };

window.start = start;
window.mutePeer = mutePeer;
window.setVolume = setVolume;
window.toggleMuteSelf = toggleMuteSelf;

window.addEventListener("DOMContentLoaded", async () => {
  const startBtn = document.querySelector("#startButton");
  const nameInput = document.getElementById("clientIdInput");
  window.handleStartOrEnd = handleStartOrEnd;
  if (startBtn && nameInput) {
    startBtn.textContent = "Start Call";
    startBtn.onclick = handleStartOrEnd;
  }
  await handleStartOrEnd();
});

export function setClientId(newId) {
  myId = newId;
  localStorage.setItem("clientId", myId);
  updatePeerListUI();
  if (wsReady) {
    safeSend({ type: "hello", id: myId });
  }
}

export { myId };
