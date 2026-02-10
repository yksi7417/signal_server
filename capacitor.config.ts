import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.mahjong.game',
  appName: 'Mahjong',
  webDir: 'static',
  // Server mode: iOS app loads from deployed server (instant updates, no resubmission)
  server: {
    url: 'https://signal-server-eo-7uq.fly.dev',
    cleartext: false,
  },
  ios: {
    scheme: 'Mahjong',
    contentInset: 'always',
  },
  plugins: {
    SplashScreen: {
      launchAutoHide: true,
      androidScaleType: 'CENTER_CROP',
      splashFullScreen: true,
      splashImmersive: true,
      backgroundColor: '#0a5a25',
    },
  },
};

export default config;
