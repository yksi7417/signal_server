import { initializeAudio } from './audioManager.js';
import { myId } from './signaling.js';

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
    const resultElement = document.getElementById(`full-result-${myId}`);
    if (resultElement) {
      const resultData = JSON.parse(ev.detail); 
      resultElement.textContent = `Full: ${resultData.text}`;
    }
  });

  recognizer.addEventListener("partialResult", ev => {
    const partialResultElement = document.getElementById(`partial-result-${myId}`);
    if (partialResultElement) {
        const resultData = JSON.parse(ev.detail); 
        partialResultElement.textContent = `Partial: ${resultData.partial}`;
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
