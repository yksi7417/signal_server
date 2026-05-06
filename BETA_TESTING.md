# Mahjong+× — Beta testing on a phone

Two paths. Pick one (or do both — they're independent).

| | Path A — Sideload | Path B — TestFlight |
|---|---|---|
| Cost | Free | $99/year (Apple Developer Program) |
| Setup time | ~10 min | ~1–2 days end-to-end (mostly Apple's enrollment review) |
| Reach | Your phone only | Up to 10,000 testers via email invite |
| App lifespan | 7 days, then re-sign | 90 days per build |
| Approval gate | None | Brief beta review for external testers |
| Best for | Smoke-testing on your own device | Real beta with friends / target demographic |

---

## Path A — Sideload to your own iPhone

You need: your iPhone, a USB-C cable, an Apple ID (free is fine).

1. **Connect your iPhone to the Mac.** Unlock it, tap *Trust This Computer* if prompted.

2. **Open the project in Xcode:**
   ```bash
   open MahjongPlusX.xcodeproj
   ```

3. **Add your Apple ID once:** Xcode → Settings → Accounts → `+` → Apple ID. Sign in.

4. **Configure signing:**
   - Select the `MahjongPlusX` project in the file navigator
   - Select the `MahjongPlusX` target → **Signing & Capabilities** tab
   - Check **Automatically manage signing**
   - **Team**: pick `<Your Name> (Personal Team)`
   - **Bundle Identifier**: change to something unique like `com.<yourname>.mahjongplusx`
     (Apple requires uniqueness per-Apple-ID, and `com.mahjongplusx.app` may be taken)

5. **Pick your iPhone as the destination** (top toolbar, next to ⏵ button) and hit **⌘R**.
   - First time: Xcode does a code-sign / provisioning dance; if it asks to register the device, say yes.

6. **On the phone, trust the developer:**
   Settings → General → VPN & Device Management → tap your Apple-ID email → *Trust*

7. **Launch from the home screen.** Done.

After 7 days the app stops launching. Plug back in and ⌘R again to refresh the signature.

---

## Path B — TestFlight

For sending invites to 1–10,000 testers without them needing to plug in. The right answer for real beta.

### One-time setup

#### 1. Enroll in the Apple Developer Program
- [developer.apple.com/programs](https://developer.apple.com/programs) → Enroll → $99/year
- "Individual" enrollment is fine; switch to "Organization" later if you want a company name on the App Store
- Approval is usually <24h

#### 2. Find your Team ID
- [appstoreconnect.apple.com](https://appstoreconnect.apple.com) → top-right name dropdown → **Membership**
- Copy the **Team ID** (10-char alphanumeric, e.g. `8K7L3M9P2X`)

#### 3. Register the bundle identifier
- [developer.apple.com/account/resources/identifiers](https://developer.apple.com/account/resources/identifiers) → `+` → App IDs → App
- **Description**: `Mahjong Plus X`
- **Bundle ID**: explicit, e.g. `com.<yourname>.mahjongplusx`
- No special capabilities needed for MVP

#### 4. Create the app in App Store Connect
- [appstoreconnect.apple.com/apps](https://appstoreconnect.apple.com/apps) → `+` → New App
- **Platform**: iOS
- **Name**: `Mahjong Plus X` (App Store doesn't allow `+×` in names)
- **Bundle ID**: pick the one you just registered
- **SKU**: anything unique like `mahjongplusx-001`

#### 5. Create an App Store Connect API key
- [appstoreconnect.apple.com → Users and Access → Keys](https://appstoreconnect.apple.com/access/api)
- Generate a new key with the **App Manager** role
- Download the `.p8` file (you can only download it ONCE)
- Note the **Key ID** (10-char) and **Issuer ID** (UUID)

#### 6. Wire your team into the build
Edit `Project.env` at the repo root:
```bash
DEVELOPMENT_TEAM=8K7L3M9P2X
BUNDLE_ID=com.yourname.mahjongplusx
MARKETING_VERSION=0.1.0
BUILD_NUMBER=1
```

#### 7. Set the API-key env vars in your shell
Put these in `~/.zshrc` (or wherever) so every shell has them:
```bash
export APP_STORE_KEY_ID="ABC123XYZ9"
export APP_STORE_ISSUER_ID="69a6de70-aaaa-bbbb-cccc-1234567890ab"
export APP_STORE_KEY_PATH="$HOME/secrets/AuthKey_ABC123XYZ9.p8"
```
(Don't commit the `.p8` to the repo. Keep it somewhere safe.)

### Every release

```bash
./scripts/release-testflight.sh
```

That single script does the lot:
1. Bumps `BUILD_NUMBER` in `Project.env` (TestFlight rejects duplicates)
2. Regenerates the Xcode project with the new env baked in
3. Archives a Release build for `iphoneos`
4. Exports an `.ipa` using `scripts/ExportOptions.plist`
5. Uploads to App Store Connect via `xcrun altool`

Flags:
- `--no-bump`     don't increment build number (use the same one again — only useful for re-trying a failed upload after an Apple processing glitch)
- `--no-upload`   archive + export but skip the upload (gives you `build/export/MahjongPlusX.ipa` for manual inspection)

Allow ~5–15 minutes after a successful upload before the build appears in App Store Connect → TestFlight (Apple processes the symbols and re-signs).

### Inviting testers

[appstoreconnect.apple.com](https://appstoreconnect.apple.com) → your app → **TestFlight** tab.

**Internal testers** (instant, no Apple review):
- Up to 100, all need an App Store Connect role on your team
- They get the build immediately after processing finishes

**External testers** (up to 10,000):
- Add by email
- First build per `MARKETING_VERSION` triggers a beta review (~24h first time, near-instant after)
- Testers get an email with a TestFlight invite link

Testers download the **TestFlight** app from the App Store, accept the email invite, install your build. Builds last **90 days** before they need to update.

---

## What's in the box

- `Project.env` — committed defaults; override per-shell with env vars
- `scripts/run-ios.sh` — local simulator workflow (Path A's day-to-day)
- `scripts/bump-build.sh` — bumps `BUILD_NUMBER` (auto-called by release script)
- `scripts/release-testflight.sh` — full Path B pipeline
- `scripts/ExportOptions.plist` — `xcodebuild -exportArchive` config
- `App/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png` — placeholder app icon (regenerate via `swift run icon-gen`; replace before public release)

## Troubleshooting

**"No team selected" / "Signing requires a development team"**
- `DEVELOPMENT_TEAM` is empty in `Project.env`. Fill it in and re-run.

**TestFlight: "The bundle version must be greater than the previously uploaded version"**
- Apple rejected because `BUILD_NUMBER` clashes with an existing upload. Run `./scripts/bump-build.sh` and retry, or `./scripts/release-testflight.sh` (which auto-bumps).

**TestFlight: "Missing Push Notification Entitlement" or other capability errors**
- The app doesn't use these — those warnings are noise. Real errors appear under "Asset validation".

**Build fails with "Provisioning profile doesn't include the currently selected device"**
- Either the bundle ID isn't registered in your Developer account, or your team can't auto-create profiles. Open in Xcode once (`open MahjongPlusX.xcodeproj`), let it auto-fix, close, then re-run from CLI.

**App icon is empty in TestFlight**
- The `AppIcon-1024.png` is a placeholder. Replace it with a real 1024×1024 PNG at the same path and rerun.
