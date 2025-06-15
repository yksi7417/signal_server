let sharedAudioContext;
let sharedMediaStream;

export async function initializeAudio() {
  if (!sharedAudioContext) {
    sharedAudioContext = new AudioContext();
  }
  if (!sharedMediaStream) {
    sharedMediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  }
  return { sharedAudioContext, sharedMediaStream };
}
