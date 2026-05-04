#!/bin/bash
# setup_ios.sh - Sets up the Capacitor iOS project for Mahjong
# Run this from the signal_server project root directory
#
# Prerequisites:
#   - Node.js installed (you have v22)
#   - Xcode installed from the Mac App Store
#   - An iPhone connected via USB (for device testing)
#
# Usage:
#   chmod +x setup_ios.sh
#   ./setup_ios.sh

set -e

echo "=== Step 1: Checking prerequisites ==="

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed. Install it from https://nodejs.org"
    exit 1
fi
echo "Node.js: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not installed."
    exit 1
fi
echo "npm: $(npm --version)"

# Check Xcode
if ! command -v xcodebuild &> /dev/null; then
    echo "ERROR: Xcode is not installed. Install it from the Mac App Store."
    exit 1
fi
echo "Xcode: $(xcodebuild -version | head -1)"

# Check that we're in the right directory
if [ ! -f "capacitor.config.ts" ]; then
    echo "ERROR: capacitor.config.ts not found. Run this script from the signal_server project root."
    exit 1
fi
echo "Project directory: OK"

echo ""
echo "=== Step 2: Installing Capacitor packages ==="
npm install @capacitor/core @capacitor/cli @capacitor/ios

echo ""
echo "=== Step 3: Adding iOS platform ==="
if [ -d "ios" ]; then
    echo "ios/ directory already exists, skipping 'cap add ios'."
    echo "If you want to recreate it, delete the ios/ folder and re-run this script."
else
    npx cap add ios
fi

echo ""
echo "=== Step 4: Syncing Capacitor ==="
npx cap sync ios

echo ""
echo "=== Step 5: Done! ==="
echo ""
echo "Next steps (manual):"
echo "  1. Open Xcode:  npx cap open ios"
echo "  2. In Xcode: select the 'App' target -> 'Signing & Capabilities'"
echo "  3. Check 'Automatically manage signing'"
echo "  4. For Team: click 'Add an Account...' and sign in with your Apple ID"
echo "  5. Connect your iPhone via USB and select it as the build target"
echo "  6. Press Cmd+R to build and run"
echo "  7. On your iPhone: Settings -> General -> VPN & Device Management"
echo "     -> tap your Apple ID -> tap 'Trust'"
echo "  8. Relaunch the app on your iPhone!"
echo ""
echo "NOTE: Free provisioning apps expire after 7 days."
echo "      Re-run from Xcode (Cmd+R) to re-deploy."
