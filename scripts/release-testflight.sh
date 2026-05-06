#!/bin/bash
# Mahjong+× — TestFlight release.
#
# 1. Bumps BUILD_NUMBER in Project.env.
# 2. Regenerates the Xcode project with the new env vars baked in.
# 3. Archives a Release build for iOS.
# 4. Exports an .ipa with App Store Connect signing.
# 5. Uploads to App Store Connect via altool (App Store Connect API key).
#
# Prerequisites (set BEFORE running):
#   - Project.env has DEVELOPMENT_TEAM filled in (10-char Team ID)
#   - Project.env has BUNDLE_ID matching your registered identifier
#   - One App Store Connect API key, downloaded as .p8, available via env:
#       APP_STORE_KEY_ID       (10-char key id)
#       APP_STORE_ISSUER_ID    (UUID)
#       APP_STORE_KEY_PATH     (full path to AuthKey_<KEY_ID>.p8)
#
# Usage:
#   ./scripts/release-testflight.sh                    # archive + export + upload
#   ./scripts/release-testflight.sh --no-upload        # archive + export only
#   ./scripts/release-testflight.sh --no-bump          # don't bump build number
set -euo pipefail

cd "$(dirname "$0")/.."
SCRIPT_DIR="$(pwd)/scripts"

# Parse flags.
DO_BUMP=true
DO_UPLOAD=true
for arg in "$@"; do
  case "$arg" in
    --no-upload) DO_UPLOAD=false ;;
    --no-bump)   DO_BUMP=false ;;
    *)           echo "Unknown arg: $arg"; exit 1 ;;
  esac
done

# 1. Bump build number.
if [ "$DO_BUMP" = true ]; then
  "$SCRIPT_DIR/bump-build.sh"
fi

# 2. Source env + regenerate project.
set -a
source Project.env
set +a

if [ -z "$DEVELOPMENT_TEAM" ]; then
  echo "✗ DEVELOPMENT_TEAM is empty in Project.env — fill it before releasing"
  exit 1
fi

echo "→ Regenerating Xcode project (team=$DEVELOPMENT_TEAM, bundle=$BUNDLE_ID, build=$BUILD_NUMBER)"
xcodegen generate >/dev/null

# 3. Archive.
ARCHIVE_PATH="build/MahjongPlusX.xcarchive"
EXPORT_PATH="build/export"
mkdir -p build
rm -rf "$ARCHIVE_PATH" "$EXPORT_PATH"

echo "→ Archiving (Release, iOS)"
xcodebuild \
  -project MahjongPlusX.xcodeproj \
  -scheme MahjongPlusX \
  -sdk iphoneos \
  -configuration Release \
  -archivePath "$ARCHIVE_PATH" \
  -allowProvisioningUpdates \
  archive | xcbeautify --quiet 2>/dev/null || xcodebuild \
    -project MahjongPlusX.xcodeproj \
    -scheme MahjongPlusX \
    -sdk iphoneos \
    -configuration Release \
    -archivePath "$ARCHIVE_PATH" \
    -allowProvisioningUpdates \
    archive

# 4. Export.
echo "→ Exporting .ipa"
xcodebuild -exportArchive \
  -archivePath "$ARCHIVE_PATH" \
  -exportPath "$EXPORT_PATH" \
  -exportOptionsPlist "$SCRIPT_DIR/ExportOptions.plist" \
  -allowProvisioningUpdates

IPA_PATH="$EXPORT_PATH/MahjongPlusX.ipa"
if [ ! -f "$IPA_PATH" ]; then
  echo "✗ Export didn't produce $IPA_PATH"
  ls -la "$EXPORT_PATH" || true
  exit 1
fi
echo "✓ Built $IPA_PATH"

# 5. Upload.
if [ "$DO_UPLOAD" = false ]; then
  echo "↪ Skipping upload (--no-upload)"
  echo "  IPA at: $IPA_PATH"
  exit 0
fi

: "${APP_STORE_KEY_ID:?Set APP_STORE_KEY_ID env var}"
: "${APP_STORE_ISSUER_ID:?Set APP_STORE_ISSUER_ID env var}"
: "${APP_STORE_KEY_PATH:?Set APP_STORE_KEY_PATH env var}"

# altool wants the key file in ~/.appstoreconnect/private_keys/AuthKey_<id>.p8.
PRIV_DIR="$HOME/.appstoreconnect/private_keys"
mkdir -p "$PRIV_DIR"
KEY_BASENAME="AuthKey_${APP_STORE_KEY_ID}.p8"
if [ ! -f "$PRIV_DIR/$KEY_BASENAME" ]; then
  cp "$APP_STORE_KEY_PATH" "$PRIV_DIR/$KEY_BASENAME"
  echo "→ Installed API key at $PRIV_DIR/$KEY_BASENAME"
fi

echo "→ Uploading to App Store Connect"
xcrun altool --upload-app \
  -f "$IPA_PATH" \
  -t ios \
  --apiKey "$APP_STORE_KEY_ID" \
  --apiIssuer "$APP_STORE_ISSUER_ID"

echo "✓ Upload accepted. Build will appear in App Store Connect → TestFlight"
echo "  in 5–15 minutes after Apple finishes processing."
