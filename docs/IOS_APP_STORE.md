# iOS App Store Deployment Guide

This guide covers deploying the Mahjong webapp as a native iOS app via Capacitor.

## Architecture

The iOS app uses **Capacitor server mode** — it loads content from the deployed
fly.dev server rather than bundling static files. This means web updates are
instant (no App Store resubmission needed for web changes).

## Prerequisites

1. **Apple Developer Program** membership ($99/year) — [developer.apple.com](https://developer.apple.com)
2. **macOS** with **Xcode 15+** installed
3. **Node.js 18+** and npm

## Step 1: Create App ID

1. Go to [Apple Developer Portal](https://developer.apple.com/account/resources/identifiers/list)
2. Create a new App ID:
   - Platform: iOS
   - Bundle ID: `com.mahjong.game` (matches `capacitor.config.ts`)
   - Enable capabilities: **Sign in with Apple**

## Step 2: Create Services ID (for SIWA on web)

1. In the Developer Portal, create a new Services ID
2. Configure the web authentication domain and redirect URL:
   - Domain: `signal-server-eo-7uq.fly.dev`
   - Return URL: `https://signal-server-eo-7uq.fly.dev/api/auth/apple/callback`
3. Note the Services ID — set as `APPLE_CLIENT_ID` env var on fly.dev

## Step 3: Initialize Capacitor

```bash
# Install Capacitor CLI
npm install @capacitor/core @capacitor/cli @capacitor/ios

# Initialize (config already exists in capacitor.config.ts)
npx cap add ios
```

## Step 4: Configure Xcode Project

```bash
# Open the iOS project in Xcode
npx cap open ios
```

In Xcode:
1. Select the project target
2. Under **Signing & Capabilities**:
   - Set your Team
   - Set Bundle Identifier to `com.mahjong.game`
   - Add capability: **Sign in with Apple**
3. Under **General**:
   - Set Display Name to "Mahjong"
   - Set Deployment Target to iOS 15.0+
   - Set Device Orientation to Landscape

## Step 5: App Icons

Replace the default Capacitor app icons with the game icons:
- Use an icon generator tool to create all required sizes from `icon-512.png`
- Place in `ios/App/App/Assets.xcassets/AppIcon.appiconset/`

## Step 6: Environment Variables (fly.dev)

Set these secrets on the fly.dev deployment:

```bash
fly secrets set APPLE_CLIENT_ID="com.mahjong.game"
fly secrets set APPLE_TEAM_ID="YOUR_TEAM_ID"
```

## Step 7: TestFlight Beta

1. In Xcode: Product > Archive
2. Upload to App Store Connect
3. In [App Store Connect](https://appstoreconnect.apple.com):
   - Create the app entry
   - Submit build to TestFlight
   - Add beta testers

## Step 8: App Store Submission

1. Complete the App Store listing:
   - Screenshots (landscape, various device sizes)
   - Description, keywords, category (Games > Board)
   - Age rating
   - Privacy policy URL
2. Submit for review

## App Review Considerations

- **SIWA requirement**: Apple requires Sign in with Apple if you offer any
  third-party login (App Store guideline 4.8). Our app offers SIWA as the
  primary auth method, satisfying this requirement.
- **Guest mode**: The app works without login (guest mode). Ensure this is
  mentioned in the review notes.
- **Web content**: Since the app loads from a server, note this in the review
  submission. Apple allows this for apps that are essentially web apps wrapped
  in a native shell, provided they add native value (SIWA, PWA features).

## Updating the App

Since the app uses server mode:
- **Web changes** (HTML, CSS, JS, Python backend): Deploy to fly.dev — changes
  are live immediately, no App Store update needed.
- **Native changes** (Capacitor config, iOS capabilities): Requires new Xcode
  build + App Store submission.

## Troubleshooting

### SIWA not working in simulator
Sign in with Apple requires a real device for testing. Use TestFlight builds.

### App rejected for web content
Ensure the app provides value beyond a simple web wrapper. The SIWA integration
and PWA capabilities (offline support, home screen icon) provide native value.

### Network errors in app
Check that `server.url` in `capacitor.config.ts` is correct and the fly.dev
app is running. The app requires network connectivity in server mode.
