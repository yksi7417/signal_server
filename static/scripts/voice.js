import { initializeAudio } from './audioManager.js';
import { myId } from './signaling.js';

const modelPath = "/static/model"
const modelExt  = ".tar.gz";
const modelMap  = {
  "Chinese": "vosk-model-small-cn-0.22",
  "English": "vosk-model-small-en-us-0.15",
}

async function createRecognizer(language){
  const modelName = modelMap[language];
  const module = await loadVosklet();
  const model = await module.createModel(`${modelPath}/${modelName}${modelExt}`, language, modelName);
// const targetWords = [
//   "Eat", "Bump", "Hit", "Throw", "Woo"
// ];
// const recognizer = await module.createRecognizerWithGrm(model, 16000,
//   JSON.stringify(targetWords));
  return await module.createRecognizer(model, sharedAudioContext.sampleRate);
}

async function start() {
  const { sharedAudioContext, sharedMediaStream } = await initializeAudio();

  let micNode = sharedAudioContext.createMediaStreamSource(sharedMediaStream);
  let recognizer = await createRecognizer('English')

  recognizer.addEventListener("result", ev => {
    const resultElement = document.getElementById(`full-result-${myId}`);
    if (resultElement) {
      const resultData = JSON.parse(ev.detail); // Parse the JSON string
      const recognizedText = resultData.text;

      resultElement.textContent = `Full: ${recognizedText}`;
      console.log(`Recognized command: ${recognizedText}`);
    }
  });

  recognizer.addEventListener("partialResult", ev => {
    const partialResultElement = document.getElementById(`partial-result-${myId}`);
    if (partialResultElement) {
      const partialData = JSON.parse(ev.detail); // Parse the JSON string
      partialResultElement.textContent = `Partial: ${partialData.partial}`;
    }
  });

  const transferer = await module.createTransferer(sharedAudioContext, 128 * 150);
  transferer.port.onmessage = ev => recognizer.acceptWaveform(ev.data);
  micNode.connect(transferer);
}

export { start };
