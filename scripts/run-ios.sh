#!/bin/bash
# Mahjong+× — regenerate, build, install, and launch on the iOS simulator.
# Usage: ./scripts/run-ios.sh
set -euo pipefail

SIM_NAME="${SIM_NAME:-iPhone 16e}"
SIM_OS="${SIM_OS:-26.2}"

# Source build-time config (DEVELOPMENT_TEAM, BUNDLE_ID, MARKETING_VERSION,
# BUILD_NUMBER) so xcodegen can substitute them into project.yml.
if [ -f Project.env ]; then
  set -a
  # shellcheck source=../Project.env
  source Project.env
  set +a
fi
BUNDLE_ID="${BUNDLE_ID:-com.mahjongplusx.app}"

echo "→ Regenerating Xcode project (bundle=$BUNDLE_ID, build=${BUILD_NUMBER:-?})"
xcodegen generate >/dev/null

echo "→ Building for $SIM_NAME (iOS $SIM_OS)"
xcodebuild -project MahjongPlusX.xcodeproj \
  -scheme MahjongPlusX \
  -destination "platform=iOS Simulator,name=$SIM_NAME,OS=$SIM_OS" \
  -quiet build

# Find the booted simulator (or boot one).
SIM_ID=$(xcrun simctl list devices available \
  | grep -F "$SIM_NAME" \
  | grep -oE "\([A-F0-9-]{36}\)" \
  | head -1 \
  | tr -d '()')

if [ -z "$SIM_ID" ]; then
  echo "✗ Could not find simulator named '$SIM_NAME'"
  exit 1
fi

echo "→ Booting simulator $SIM_ID"
xcrun simctl boot "$SIM_ID" 2>/dev/null || true
open -a Simulator

# Find the .app
APP_PATH=$(find ~/Library/Developer/Xcode/DerivedData/MahjongPlusX-*/Build/Products/Debug-iphonesimulator -name "MahjongPlusX.app" -type d 2>/dev/null | head -1)
if [ -z "$APP_PATH" ]; then
  echo "✗ Couldn't find built MahjongPlusX.app"
  exit 1
fi

echo "→ Installing $APP_PATH"
xcrun simctl install "$SIM_ID" "$APP_PATH"

echo "→ Launching"
xcrun simctl terminate "$SIM_ID" "$BUNDLE_ID" 2>/dev/null || true
xcrun simctl launch "$SIM_ID" "$BUNDLE_ID"

echo "✓ App is running on $SIM_NAME"
