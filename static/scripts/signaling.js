const peers = {};
const pendingCandidates = {};
const peerJoinTimes = {};
let myId = "client-" + Math.floor(Math.random() * 10000);
let localStream;
let ws;
let wsReady = false;

const peerList = document.getElementById("peerList");
const dingSound = document.getElementById("ding");

function updatePeerListUI() {
  peerList.innerHTML = "";
  for (const [id, pc] of Object.entries(peers)) {
    const li = document.createElement("li");
    li.className = "peer-entry";
    li.innerHTML = `
      <div class="mic-indicator" id="mic-${id}"></div>
      <strong>${id}</strong>
      <span>🕒 ${peerJoinTimes[id]?.toLocaleTimeString() || ""}</span>
      <span id="latency-${id}">⏱️ --</span>
      <button onclick="mutePeer('${id}')">🔇</button>
      <input type="range" min="0" max="1" step="0.01" value="1" onchange="setVolume('${id}', this.value)">
    `;
    peerList.appendChild(li);
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
    const audio = new Audio();
    audio.srcObject = streams[0];
    audio.autoplay = true;
    audio.id = `audio-${peerId}`;
    document.body.appendChild(audio);
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
  localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  monitorMicActivity(localStream);

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
}

window.start = start;
window.mutePeer = mutePeer;
window.setVolume = setVolume;
