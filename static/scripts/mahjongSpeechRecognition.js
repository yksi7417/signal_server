/**
 * Mahjong Speech Recognition for iPhone/Safari
 * Provides voice command recognition for Mahjong game actions
 */

// Mahjong-specific keywords and commands
const MAHJONG_COMMANDS = {
  // Game actions
  '食糊': 'win',
  '糊': 'win',
  '食': 'eat',
  '碰': 'pong',
  '開槓': 'kong',
  '槓': 'kong',
  '上': 'chi',
  '過': 'pass',
  '跳過': 'pass',
  
  // Tiles - dots/circles (筒)
  '一筒': '1-dots',
  '二筒': '2-dots',
  '三筒': '3-dots',
  '四筒': '4-dots',
  '五筒': '5-dots',
  '六筒': '6-dots',
  '七筒': '7-dots',
  '八筒': '8-dots',
  '九筒': '9-dots',
  
  // Tiles - bamboo (索)
  '一索': '1-bamboo',
  '二索': '2-bamboo',
  '三索': '3-bamboo',
  '四索': '4-bamboo',
  '五索': '5-bamboo',
  '六索': '6-bamboo',
  '七索': '7-bamboo',
  '八索': '8-bamboo',
  '九索': '9-bamboo',
  
  // Tiles - characters (萬)
  '一萬': '1-characters',
  '二萬': '2-characters',
  '三萬': '3-characters',
  '四萬': '4-characters',
  '五萬': '5-characters',
  '六萬': '6-characters',
  '七萬': '7-characters',
  '八萬': '8-characters',
  '九萬': '9-characters',
  
  // Wind tiles
  '東': 'east-wind',
  '南': 'south-wind',
  '西': 'west-wind',
  '北': 'north-wind',
  
  // Dragon tiles
  '紅中': 'red-dragon',
  '發財': 'green-dragon',
  '白板': 'white-dragon'
};

class MahjongSpeechRecognition {
  constructor() {
    this.recognition = null;
    this.isSupported = false;
    this.isListening = false;
    this.onCommandCallback = null;
    this.onErrorCallback = null;
    this.onStatusCallback = null;
    
    this.init();
  }
  
  init() {
    // Check for Web Speech API support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.warn('Web Speech API not supported in this browser');
      this.isSupported = false;
      return;
    }
    
    this.isSupported = true;
    this.recognition = new SpeechRecognition();
    this.setupRecognition();
  }
    setupRecognition() {
    if (!this.recognition) return;
    
    // Configure recognition settings
    this.recognition.lang = 'zh-HK'; // Cantonese (Hong Kong)
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.maxAlternatives = 3;
    
    // iOS/Safari specific optimizations
    if (navigator.userAgent.includes('iPhone') || navigator.userAgent.includes('iPad')) {
      this.recognition.continuous = false; // iOS works better with non-continuous mode
      console.log('📱 iOS device detected, using optimized settings');
    }
    
    // Set up event handlers
    this.recognition.onstart = () => {
      this.isListening = true;
      console.log('🎤 Mahjong speech recognition started');
      this.notifyStatus('listening', 'Speech recognition started');
    };
    
    this.recognition.onresult = (event) => {
      this.handleSpeechResult(event);
    };
    
    this.recognition.onerror = (event) => {
      console.error('🚨 Speech recognition error:', event.error);
      this.notifyError(event.error, `Recognition error: ${event.error}`);
      
      // Auto-restart on certain errors (but not on iOS due to permissions)
      const isIOS = navigator.userAgent.includes('iPhone') || navigator.userAgent.includes('iPad');
      if (!isIOS && (event.error === 'network' || event.error === 'no-speech')) {
        setTimeout(() => {
          if (this.isListening) {
            this.start();
          }
        }, 1000);
      }
    };
    
    this.recognition.onend = () => {
      this.isListening = false;
      console.log('🛑 Speech recognition ended');
      this.notifyStatus('stopped', 'Speech recognition stopped');
      
      // Auto-restart if we were supposed to be listening (not on iOS)
      const isIOS = navigator.userAgent.includes('iPhone') || navigator.userAgent.includes('iPad');
      if (!isIOS && this.shouldRestart) {
        setTimeout(() => this.start(), 500);
      }
    };
  }
  
  handleSpeechResult(event) {
    const results = event.results;
    const lastResult = results[results.length - 1];
    
    if (!lastResult) return;
    
    // Get the best transcript
    const transcript = lastResult[0].transcript.trim();
    const confidence = lastResult[0].confidence;
    const isFinal = lastResult.isFinal;
    
    console.log(isFinal ? '✅ Final:' : '⏳ Interim:', transcript, `(${(confidence * 100).toFixed(1)}%)`);
    
    // Process the transcript for Mahjong commands
    if (isFinal && transcript) {
      this.processCommand(transcript, confidence);
    }
    
    // Update UI with partial results
    this.updateUI(transcript, isFinal, confidence);
  }
  
  processCommand(transcript, confidence) {
    // Convert to lowercase for matching
    const normalizedTranscript = transcript.toLowerCase().trim();
    
    // Find matching Mahjong commands
    const matchedCommands = [];
    
    for (const [keyword, action] of Object.entries(MAHJONG_COMMANDS)) {
      if (normalizedTranscript.includes(keyword.toLowerCase())) {
        matchedCommands.push({
          keyword,
          action,
          confidence: confidence || 0
        });
      }
    }
    
    // If we found commands, execute the most confident one
    if (matchedCommands.length > 0) {
      const bestMatch = matchedCommands.reduce((best, current) => 
        current.confidence > best.confidence ? current : best
      );
      
      console.log('🎯 Mahjong command detected:', bestMatch);
      this.notifyCommand(bestMatch, transcript);
    }
  }
    updateUI(transcript, isFinal, confidence) {
    // Update the speech results in the UI
    const partialElement = document.getElementById('speechPartial');
    const fullElement = document.getElementById('speechFinal');
    
    if (isFinal && fullElement) {
      const confidenceText = confidence ? ` (${(confidence * 100).toFixed(1)}%)` : '';
      fullElement.textContent = `Final: ${transcript}${confidenceText}`;
      fullElement.style.color = '#2E7D32';
    } else if (!isFinal && partialElement) {
      partialElement.textContent = `Listening: ${transcript}`;
      partialElement.style.color = '#666';
    }
    
    // Clear partial result when we get a final result
    if (isFinal && partialElement) {
      setTimeout(() => {
        partialElement.textContent = 'Listening for Mahjong commands...';
      }, 2000);
    }
  }
  
  start() {
    if (!this.isSupported) {
      console.warn('Speech recognition not supported');
      return false;
    }
    
    if (this.isListening) {
      console.log('Speech recognition already running');
      return true;
    }
    
    try {
      this.shouldRestart = true;
      this.recognition.start();
      return true;
    } catch (error) {
      console.error('Failed to start speech recognition:', error);
      this.notifyError('start-failed', `Failed to start: ${error.message}`);
      return false;
    }
  }
  
  stop() {
    if (!this.recognition || !this.isListening) {
      return;
    }
    
    this.shouldRestart = false;
    this.recognition.stop();
  }
  
  toggle() {
    if (this.isListening) {
      this.stop();
    } else {
      this.start();
    }
  }
  
  // Event callback setters
  onCommand(callback) {
    this.onCommandCallback = callback;
  }
  
  onError(callback) {
    this.onErrorCallback = callback;
  }
  
  onStatus(callback) {
    this.onStatusCallback = callback;
  }
  
  // Internal notification methods
  notifyCommand(command, originalText) {
    if (this.onCommandCallback) {
      this.onCommandCallback({
        command: command.action,
        keyword: command.keyword,
        confidence: command.confidence,
        originalText: originalText,
        timestamp: new Date()
      });
    }
  }
  
  notifyError(errorCode, message) {
    if (this.onErrorCallback) {
      this.onErrorCallback({
        error: errorCode,
        message: message,
        timestamp: new Date()
      });
    }
  }
  
  notifyStatus(status, message) {
    if (this.onStatusCallback) {
      this.onStatusCallback({
        status: status,
        message: message,
        timestamp: new Date()
      });
    }
  }
  
  // Utility methods
  isSupported() {
    return this.isSupported;
  }
  
  isActive() {
    return this.isListening;
  }
  
  getSupportedCommands() {
    return Object.keys(MAHJONG_COMMANDS);
  }
}

// Export for use in other modules
export { MahjongSpeechRecognition, MAHJONG_COMMANDS };
