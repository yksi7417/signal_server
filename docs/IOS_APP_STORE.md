# iOS App Store Deployment Guide

Complete step-by-step guide to ship the Mahjong webapp to the iOS App Store using Capacitor.

---

## How It Works

The app uses **Capacitor in server mode**. The iOS app is a thin native shell (WKWebView) that loads all content from your fly.dev backend at `https://signal-server-eo-7uq.fly.dev`. This means:

- Web changes (HTML/CSS/JS/Python) deploy instantly via `fly deploy` — no App Store re-review
- The native shell only needs updating for Capacitor version bumps or new native plugins
- Sign in with Apple works natively inside the WKWebView

```
┌─────────────────────────────────┐
│  iOS App (Capacitor shell)      │
│  ┌───────────────────────────┐  │
│  │  WKWebView                │  │
│  │  loads: signal-server-    │  │
│  │  eo-7uq.fly.dev/game     │  │
│  └───────────────────────────┘  │
│  Native: SIWA, status bar,      │
│  splash screen, orientation     │
└─────────────────────────────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────┐
│  fly.dev (Python + aiohttp)     │
│  - Game logic                   │
│  - SIWA token verification      │
│  - SQLite user/stats DB         │
│  - Static assets (HTML/CSS/JS)  │
└─────────────────────────────────┘
```

---

## Prerequisites

Before starting, you need:

| Requirement | Where to get it | Cost |
|---|---|---|
| Apple Developer Program membership | [developer.apple.com/programs](https://developer.apple.com/programs/) | $99/year |
| Mac with macOS 14 Sonoma or later | — | — |
| Xcode 15+ (from Mac App Store) | Mac App Store → search "Xcode" | Free |
| Node.js 18+ and npm | [nodejs.org](https://nodejs.org/) or `brew install node` | Free |
| Fly CLI (`flyctl`) | [fly.io/docs/flyctl/install](https://fly.io/docs/flyctl/install/) | Free |
| This repo cloned on your Mac | `git clone` this repo | — |

---

## Part A: Apple Developer Portal Setup

### A1. Enroll in Apple Developer Program

1. Go to [developer.apple.com/programs](https://developer.apple.com/programs/)
2. Click "Enroll" and sign in with your Apple ID
3. Complete enrollment (requires $99/year payment)
4. Wait for approval (usually instant for individuals, 24-48h for organizations)

### A2. Create an App ID

This registers your app's Bundle ID with Apple.

1. Go to [Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources/identifiers/list)
2. Click the **+** button next to "Identifiers"
3. Select **App IDs** → Continue
4. Select **App** → Continue
5. Fill in:
   - **Description**: `Mahjong Game`
   - **Bundle ID**: Select **Explicit** and enter: `com.mahjong.game`
6. Scroll down to **Capabilities**, check: **Sign in with Apple**
7. Click **Continue** → **Register**

### A3. Create a Services ID (for SIWA web authentication)

The Services ID allows your *web* backend to verify Apple identity tokens. This is separate from the App ID.

1. Still in [Identifiers](https://developer.apple.com/account/resources/identifiers/list)
2. Click **+** → select **Services IDs** → Continue
3. Fill in:
   - **Description**: `Mahjong Web Auth`
   - **Identifier**: `com.mahjong.game.web` (this becomes your `APPLE_CLIENT_ID`)
4. Click **Continue** → **Register**
5. Now click on the newly created Services ID to edit it
6. Check **Sign in with Apple** → click **Configure**
7. In the configuration dialog:
   - **Primary App ID**: Select `Mahjong Game (com.mahjong.game)`
   - **Domains and Subdomains**: `signal-server-eo-7uq.fly.dev`
   - **Return URLs**: `https://signal-server-eo-7uq.fly.dev/game`
8. Click **Save** → **Continue** → **Save**

### A4. Note your Team ID

1. Go to [Membership Details](https://developer.apple.com/account#MembershipDetailsCard)
2. Find your **Team ID** (10-character alphanumeric string, e.g. `A1B2C3D4E5`)
3. Save this — you'll need it for fly.dev secrets

---

## Part B: Configure fly.dev Backend

### B1. Create the persistent volume (if not already done)

The SQLite database needs persistent storage that survives deploys.

```bash
# Check if volume already exists
fly volumes list -a signal-server-eo-7uq

# If no volume exists, create one (1GB is plenty for SQLite)
fly volumes create mahjong_data --region iad --size 1 -a signal-server-eo-7uq
```

### B2. Set environment secrets

```bash
# Your Services ID from step A3
fly secrets set APPLE_CLIENT_ID="com.mahjong.game.web" -a signal-server-eo-7uq

# Your Team ID from step A4
fly secrets set APPLE_TEAM_ID="YOUR_TEAM_ID_HERE" -a signal-server-eo-7uq
```

### B3. Deploy the backend

```bash
# From the repo root
fly deploy -a signal-server-eo-7uq
```

### B4. Verify the backend is running

```bash
# Check app status
fly status -a signal-server-eo-7uq

# Test the leaderboard endpoint (should return empty array)
curl https://signal-server-eo-7uq.fly.dev/api/leaderboard
# Expected: {"success": true, "leaderboard": []}

# Test that the game loads
open https://signal-server-eo-7uq.fly.dev/game
```

---

## Part C: Set Up Capacitor iOS Project (on your Mac)

### C1. Install Node dependencies

```bash
# From the repo root on your Mac
npm init -y  # Only if package.json doesn't exist yet

# Install Capacitor
npm install @capacitor/core @capacitor/cli @capacitor/ios

# Optional: splash screen plugin
npm install @capacitor/splash-screen
```

### C2. Initialize Capacitor

The `capacitor.config.ts` file already exists in the repo. Just add the iOS platform:

```bash
# This creates the ios/ directory with the Xcode project
npx cap add ios
```

You should see output like:
```
[info] Adding iOS platform...
[success] iOS platform added!
```

### C3. Sync Capacitor config to the iOS project

```bash
npx cap sync ios
```

This copies your `capacitor.config.ts` settings (server URL, splash screen config, etc.) into the native iOS project.

### C4. Open in Xcode

```bash
npx cap open ios
```

This opens the `ios/App/App.xcworkspace` file in Xcode.

---

## Part D: Configure the Xcode Project

### D1. Set Signing & Team

1. In Xcode's left sidebar, click the **App** project (blue icon at the very top)
2. Select the **App** target (not the project)
3. Go to the **Signing & Capabilities** tab
4. Check **Automatically manage signing**
5. Set **Team** to your Apple Developer account
6. **Bundle Identifier** should already be `com.mahjong.game` (from capacitor.config.ts)
   - If not, change it to `com.mahjong.game`

### D2. Add Sign in with Apple capability

1. Still on the **Signing & Capabilities** tab
2. Click **+ Capability** (top left of the tab)
3. Search for "Sign in with Apple" and double-click to add it
4. You should see "Sign in with Apple" appear in the capabilities list

### D3. Set deployment target and orientation

1. Go to the **General** tab
2. Set:
   - **Display Name**: `Mahjong`
   - **Minimum Deployments**: `iOS 15.0` (supports 95%+ of active devices)
3. Under **Deployment Info** → **Device Orientation**:
   - Uncheck **Portrait**
   - Check **Landscape Left** and **Landscape Right**
   - This forces the app to landscape (matching the game's CSS Grid layout)

### D4. Configure App Transport Security

Since the app loads from your HTTPS server, ATS should work by default. But verify:

1. In the left sidebar, find `ios/App/App/Info.plist`
2. The Capacitor server URL (`https://signal-server-eo-7uq.fly.dev`) uses HTTPS, so no ATS exceptions are needed

### D5. Replace the app icon

The placeholder icons in `static/icons/` are solid green. For the App Store, you need a real icon.

1. Create a 1024x1024 PNG icon for your app (no transparency, no rounded corners — iOS adds those)
2. Go to [appicon.co](https://www.appicon.co/) or use the `makeappicon` tool
3. Upload your 1024x1024 image — it generates all required sizes
4. In Xcode: navigate to `ios/App/App/Assets.xcassets/AppIcon.appiconset/`
5. Replace the files with the generated icon set
6. Or: drag your icon set directly into Xcode's Asset Catalog editor

### D6. Configure the splash screen

The splash screen shows while the WKWebView loads your server:

1. In Xcode, navigate to `ios/App/App/Assets.xcassets/Splash.imageset/`
2. Replace with your splash image (or keep the default green background)
3. Alternatively, edit `ios/App/App/Base.lproj/LaunchScreen.storyboard` in Xcode's Interface Builder

---

## Part E: Build, Test, and Archive

### E1. Test on Simulator

1. In Xcode, select a simulator device (e.g., "iPhone 15 Pro")
2. Press **Cmd+R** (or Product → Run)
3. The app should launch and load `https://signal-server-eo-7uq.fly.dev/game`
4. Verify:
   - Game loads and is playable
   - Login overlay appears with "Sign in with Apple" and "Play as Guest"
   - "Play as Guest" dismisses the overlay and starts the game
   - Stats button works (shows empty leaderboard)

> **Note**: Sign in with Apple does NOT work in the simulator. You must test on a real device or wait for TestFlight.

### E2. Test on a real device

1. Connect your iPhone via USB
2. In Xcode, select your device from the device dropdown
3. Press **Cmd+R**
4. If prompted, trust the developer profile on your iPhone:
   Settings → General → VPN & Device Management → trust your developer certificate
5. Test Sign in with Apple on the real device

### E3. Create the archive

1. In Xcode, select **Any iOS Device (arm64)** as the build destination (not a simulator)
2. Go to **Product → Archive**
3. Wait for the build to complete (1-3 minutes)
4. The **Organizer** window opens automatically showing your archive

---

## Part F: App Store Connect Setup

### F1. Create the app in App Store Connect

1. Go to [App Store Connect](https://appstoreconnect.apple.com/)
2. Click **My Apps** → **+** → **New App**
3. Fill in:
   - **Platforms**: iOS
   - **Name**: `Mahjong` (this is the display name on the App Store)
   - **Primary Language**: English (U.S.)
   - **Bundle ID**: Select `com.mahjong.game` (from step A2)
   - **SKU**: `mahjong-game-001` (any unique string)
   - **User Access**: Full Access
4. Click **Create**

### F2. Fill in App Store listing

Under the **App Store** tab → **1.0 Prepare for Submission**:

**App Information:**
- **Subtitle**: `Hong Kong-style Mahjong` (30 chars max)
- **Category**: Games → Board
- **Content Rights**: Check "This app does not contain third-party content"

**Pricing and Availability:**
- **Price**: Free (or set your price)
- **Availability**: Select countries/regions

**Version Information:**
- **Promotional Text**: `Play classic Hong Kong Mahjong against AI opponents. Track your wins and climb the leaderboard.`
- **Description**:
  ```
  Play Hong Kong-style Mahjong against three AI opponents.

  Features:
  - Full Hong Kong Old Style scoring (faan system)
  - Smart AI opponents that claim discards (pung, kong, chow)
  - Win tracking and leaderboard
  - Sign in with Apple for persistent stats
  - Works offline after first load

  Play as a guest or sign in to track your progress.
  ```
- **Keywords**: `mahjong,hong kong,board game,tiles,faan,strategy,chinese,table game`

**Screenshots (required):**

You need screenshots for at least one device size. Recommended: capture from simulator.

| Device | Resolution |
|---|---|
| iPhone 6.7" (15 Pro Max) | 1290 x 2796 (portrait) or 2796 x 1290 (landscape) |
| iPhone 6.5" (11 Pro Max) | 1242 x 2688 or 2688 x 1242 |
| iPad Pro 12.9" (optional) | 2048 x 2732 or 2732 x 2048 |

To take simulator screenshots:
1. Run the app in Xcode on the desired simulator
2. In Simulator: **File → Screenshot** (or Cmd+S)
3. Screenshots save to Desktop

Take 3-5 screenshots showing:
1. Login screen (SIWA + guest buttons)
2. Game in progress (tiles, discards, player areas)
3. A winning hand (celebration screen with faan score)
4. Leaderboard/stats screen

**App Review Information:**
- **Sign-in required**: No (app works as guest)
- **Contact Information**: Your name, phone, email
- **Notes for reviewer**:
  ```
  This app loads its content from our server (https://signal-server-eo-7uq.fly.dev).
  It can be tested without signing in — tap "Play as Guest" on the login screen.
  Sign in with Apple is available for users who want to track their game stats.
  The game is a single-player mahjong game against AI opponents.
  ```

### F3. Privacy Policy

Apple requires a privacy policy URL. Create one that covers:

- Data collected: Apple ID (sub), optional email, game statistics
- Data usage: User identification and leaderboard
- Data storage: SQLite on fly.dev server
- Data sharing: None, no third-party analytics

Host the privacy policy as a static page. Quick options:
- Add a `/privacy` route to your app.py
- Host on GitHub Pages
- Use a free privacy policy generator

Set the URL in App Store Connect → **App Information** → **Privacy Policy URL**.

### F4. App Privacy (data disclosure)

In App Store Connect → **App Privacy**:

1. Click **Get Started**
2. "Does your app collect any data?": **Yes**
3. Data types collected:
   - **Contact Info → Email Address**:
     - Usage: App Functionality
     - Linked to user: Yes
     - Tracking: No
   - **Identifiers → User ID**:
     - Usage: App Functionality
     - Linked to user: Yes
     - Tracking: No
4. Save

---

## Part G: Upload and Submit

### G1. Upload the build from Xcode

1. In the **Organizer** window (Window → Organizer if not open)
2. Select your archive
3. Click **Distribute App**
4. Select **App Store Connect** → **Upload**
5. Leave all options checked (bitcode, symbol upload)
6. Click **Upload**
7. Wait for the upload to complete and processing to finish (5-15 minutes)

### G2. TestFlight beta testing (recommended before submission)

1. In App Store Connect → **TestFlight** tab
2. Your build should appear after processing (can take up to 30 minutes)
3. If there's a yellow warning icon, Apple may need you to answer compliance questions:
   - "Does this app use encryption?": **Yes** (HTTPS)
   - "Is it exempt?": **Yes** — it only uses standard HTTPS/TLS
4. Under **Internal Testing**:
   - Click **+** next to "Internal Testing" to create a group
   - Add yourself and any team members as testers
   - Testers will get an email invite to install via TestFlight app
5. Test thoroughly:
   - Play a full game as guest
   - Sign in with Apple
   - Play a game and verify stats are recorded
   - Check leaderboard shows your wins
   - Kill and relaunch the app — session should persist
   - Test on multiple device sizes

### G3. Submit for App Review

1. Go to App Store Connect → **App Store** tab → **1.0 Prepare for Submission**
2. Under **Build**, click **+** and select your uploaded build
3. Verify all required fields are filled (App Store Connect shows warnings for missing items)
4. Click **Add for Review** (top right)
5. Click **Submit to App Review**

### G4. Wait for review

- Typical review time: 24-48 hours (sometimes same day)
- Apple may reject and provide feedback — common issues:
  - Missing privacy policy
  - Screenshots don't match the app
  - App crashes on launch (test thoroughly!)
  - "Minimum functionality" — if Apple thinks it's just a web wrapper (see Troubleshooting)
- If rejected, fix the issue, upload a new build, and resubmit

---

## Part H: Post-Launch

### Updating the web app (no App Store review needed)

```bash
# Make your code changes, then:
git add . && git commit -m "your changes"
fly deploy -a signal-server-eo-7uq
# Changes are live immediately for all users
```

### Updating the native shell (requires App Store review)

Only needed for:
- Changing `capacitor.config.ts` settings
- Adding new Capacitor plugins (e.g., push notifications)
- Bumping Capacitor version
- Changing Xcode project settings (orientation, capabilities)

```bash
# After modifying capacitor.config.ts or native code:
npx cap sync ios
npx cap open ios
# Then: Archive → Upload → Submit new version in App Store Connect
```

### Monitoring

```bash
# Check server logs
fly logs -a signal-server-eo-7uq

# Check database
fly ssh console -a signal-server-eo-7uq
sqlite3 /app/data/mahjong.db "SELECT count(*) FROM users;"
```

---

## Troubleshooting

### "Sign in with Apple" button doesn't work

1. **On simulator**: SIWA doesn't work in simulators. Test on real device or TestFlight.
2. **On real device**: Ensure:
   - App ID has SIWA capability (step A2)
   - Xcode project has SIWA entitlement (step D2)
   - `APPLE_CLIENT_ID` env var is set correctly on fly.dev (step B2)
3. **Check server logs**: `fly logs -a signal-server-eo-7uq | grep -i apple`

### App rejected: "Minimum Functionality" (Guideline 4.2)

Apple may reject apps that are "just a web wrapper." To mitigate:
- The app uses Sign in with Apple (native capability)
- The app has a native splash screen
- The app locks to landscape orientation (native behavior)
- Mention these in the review notes

If rejected, you can:
1. Add more native features (push notifications via `@capacitor/push-notifications`)
2. Appeal the rejection with a detailed explanation of the native features
3. Consider bundling static assets locally instead of server mode

### App rejected: "Data Collection" issues

Ensure your App Privacy disclosure (step F4) matches exactly what the app collects. Apple cross-checks this against the app's actual behavior.

### White screen on launch

The app shows a white screen while loading from the server. To fix:
1. Ensure the splash screen is configured (step D6)
2. Check that `https://signal-server-eo-7uq.fly.dev` is reachable
3. Check fly.dev isn't scaled to zero: `fly status -a signal-server-eo-7uq`
4. If using `auto_stop_machines`, the first load after idle will be slow (cold start). Consider setting `min_machines_running = 1` in `fly.toml`.

### Build fails in Xcode

```bash
# Clean and rebuild
npx cap sync ios
# In Xcode: Product → Clean Build Folder (Cmd+Shift+K)
# Then: Product → Build (Cmd+B)
```

### Database not persisting across deploys

```bash
# Verify volume is mounted
fly ssh console -a signal-server-eo-7uq
ls -la /app/data/
# Should show mahjong.db

# If no volume, create one:
fly volumes create mahjong_data --region iad --size 1 -a signal-server-eo-7uq
# Then redeploy:
fly deploy -a signal-server-eo-7uq
```

---

## Quick Reference: File Locations

| File | Purpose |
|---|---|
| `capacitor.config.ts` | Capacitor configuration (server URL, app ID, splash) |
| `fly.toml` | Fly.dev deployment config (volume mount, port) |
| `mahjong_engine/auth.py` | SIWA backend (JWT verification, sessions) |
| `mahjong_engine/database.py` | SQLite database (users, stats, history) |
| `static/game/js/auth.js` | Frontend auth (SIWA flow, guest mode) |
| `static/manifest.json` | PWA manifest |
| `static/sw.js` | Service worker (caching) |
| `static/icons/` | App icons (placeholder — replace before submission) |
| `ios/` | Generated Xcode project (created by `npx cap add ios`) |

## Quick Reference: Environment Variables (fly.dev)

| Variable | Value | Purpose |
|---|---|---|
| `APPLE_CLIENT_ID` | `com.mahjong.game.web` | Services ID for SIWA web verification |
| `APPLE_TEAM_ID` | Your 10-char Team ID | Apple Developer Team identifier |
| `PORT` | `8080` (default) | Server port |
