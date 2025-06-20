# iPhone Speech Recognition for Mahjong Game

This feature adds voice command recognition specifically designed for Mahjong games when using iPhone browsers (Chrome, Firefox, or Safari).

## Features

### Supported Voice Commands

#### Game Actions
- **食糊** or **糊** - Declare win/mahjong
- **食** - Eat/claim a tile
- **碰** - Pong (claim three of a kind)
- **開槓** or **槓** - Kong (claim four of a kind)
- **上** - Chi (sequence)
- **過** or **跳過** - Pass

#### Tile Names
- **Dots/Circles (筒)**: 一筒, 二筒, 三筒, 四筒, 五筒, 六筒, 七筒, 八筒, 九筒
- **Bamboo (索)**: 一索, 二索, 三索, 四索, 五索, 六索, 七索, 八索, 九索
- **Characters (萬)**: 一萬, 二萬, 三萬, 四萬, 五萬, 六萬, 七萬, 八萬, 九萬
- **Wind Tiles**: 東, 南, 西, 北
- **Dragon Tiles**: 紅中, 發財, 白板

## How to Use

### Setup
1. Open the Mahjong game in your iPhone browser (Chrome, Firefox, or Safari)
2. Allow microphone permissions when prompted
3. Click "Start Call" to initialize the game
4. Click "🎤 Start Voice Recognition" to begin voice commands

### Usage Tips
- **Speak clearly** in Cantonese for best recognition
- **Wait for feedback** - the system will show recognized commands
- **Use natural speech** - you don't need to pause between words
- **Check the status** - green means listening, red means error

### Browser Compatibility

#### Safari (Recommended)
- Best performance on iPhone
- May require enabling "Experimental Web Platform features" in Settings > Safari > Advanced > Feature Flags

#### Chrome
- Good performance
- Requires microphone permissions

#### Firefox
- Basic support
- May have limited recognition accuracy

## Technical Details

### Language Settings
- Primary: `zh-HK` (Cantonese - Hong Kong)
- Fallback: System default language

### iOS Optimizations
- Uses non-continuous mode for better iOS compatibility
- Optimized error handling for mobile browsers
- Reduced auto-restart on iOS to prevent permission issues

### Privacy
- All speech recognition is processed locally on your device
- No voice data is sent to external servers
- Recognition uses the browser's built-in Web Speech API

## Troubleshooting

### Common Issues

1. **"Not Supported" Error**
   - Update your browser to the latest version
   - Try Safari instead of Chrome/Firefox
   - Enable experimental features in Safari

2. **No Microphone Access**
   - Check browser permissions
   - Go to Settings > Privacy & Security > Microphone
   - Allow access for your browser

3. **Poor Recognition**
   - Speak more clearly
   - Reduce background noise
   - Try speaking closer to the microphone
   - Check if Cantonese is enabled in your iOS keyboard settings

4. **Frequent Disconnections**
   - This is normal on iOS - click start again when needed
   - Avoid switching apps while using voice recognition

### iOS Settings
For best results, ensure:
- Microphone access is enabled for your browser
- Cantonese language support is installed
- Good internet connection (for initial setup)

## Integration with Game Logic

The speech recognition system triggers events that can be integrated with your Mahjong game logic:

```javascript
// Example integration
mahjongSpeech.onCommand((command) => {
  switch(command.command) {
    case 'win':
      gameEngine.declareWin();
      break;
    case 'pong':
      gameEngine.claimPong();
      break;
    // ... other commands
  }
});
```

## Future Enhancements

- Multi-language support (Mandarin, English)
- Custom wake words
- Offline recognition
- Voice feedback
- Integration with game state validation
