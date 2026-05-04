import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.mahjong.game',
  appName: 'Mahjong',
  webDir: 'static',
  // Server mode (uncomment for production: loads from deployed server for instant updates)
  // server: {
  //   url: 'https://signal-server-eo-7uq.fly.dev',
  //   cleartext: false,
  // },
  // Allow API calls to the production server from local Capacitor mode
  server: {
    allowNavigation: ['signal-server-eo-7uq.fly.dev'],
  },
  ios: {
    scheme: 'Mahjong',
    contentInset: 'always',
    allowsLinkPreview: false,
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
