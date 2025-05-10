import { initializeAudio } from './audioManager.js';

async function start() {
  const { sharedAudioContext, sharedMediaStream } = await initializeAudio();

  // Setup microphone
  let micNode = sharedAudioContext.createMediaStreamSource(sharedMediaStream);

  // Load Vosklet module, model, and recognizer
  let module = await loadVosklet();
  let model = await module.createModel("/static/model/vosk-model-small-cn-0.22.tar.gz", "Chinese", "vosk-model-small-cn-0.22");
  let recognizer = await module.createRecognizer(model, sharedAudioContext.sampleRate);

  // Listen for result and partial result
  recognizer.addEventListener("result", ev => {
    console.log("Result: ", ev.detail);
    const logArea = document.getElementById("logArea");
    if (logArea) {
      logArea.value += `Result: ${JSON.stringify(ev.detail)}\n`;
      logArea.scrollTop = logArea.scrollHeight;
    }
  });

  recognizer.addEventListener("partialResult", ev => {
    console.log("Partial result: ", ev.detail);
    const logArea = document.getElementById("logArea");
    if (logArea) {
      logArea.value += `Partial result: ${JSON.stringify(ev.detail)}\n`;
      logArea.scrollTop = logArea.scrollHeight;
    }
  });

  // Create a transferer node to get audio data on the main thread
  let transferer = await module.createTransferer(sharedAudioContext, 128 * 150);

  // Recognize data on arrival
  transferer.port.onmessage = ev => recognizer.acceptWaveform(ev.data);

  // Connect transferer to microphone
  micNode.connect(transferer);
}

export { start };
