import { initializeAudio } from './audioManager.js';
import { myId } from './signaling.js';

const modelPath = "/static/model"
const modelExt  = ".tar.gz";
const modelMap  = {
  "Chinese": "vosk-model-small-cn-0.22",
  "English": "vosk-model-small-en-us-0.15",
}

async function createModel(language){
  const modleName = modelMap[language];
  return await module.createModel(`${modelPath}/${modelName}${modelExt}`, language, modelName);

}

async function start() {
  const { sharedAudioContext, sharedMediaStream } = await initializeAudio();

  let micNode = sharedAudioContext.createMediaStreamSource(sharedMediaStream);
  let module = await loadVosklet();
  const model = createModel("English");

  // const targetWords = [
  //   "Eat", "Bump", "Hit", "Throw", "Woo"
  // ];
  // const recognizer = await module.createRecognizerWithGrm(model, 16000,
  //   JSON.stringify(targetWords));

  let recognizer = await module.createRecognizer(model, sharedAudioContext.sampleRate);

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
