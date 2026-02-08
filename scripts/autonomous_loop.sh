#!/bin/bash
# Autonomous Development Loop Runner
# Usage: ./scripts/autonomous_loop.sh [max_iterations]

set -e  # Exit on error

echo "🤖 Starting Autonomous Development Loop"
echo "========================================"

# Configuration
REPO="yksi7417/signal_server"
MAX_ITERATIONS=${1:-10}  # Default: 10 iterations
ITERATION=0

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    echo ""
    echo "🔄 Iteration $ITERATION/$MAX_ITERATIONS"
    echo "========================================"

    # Check for open bugs
    echo "📋 Checking for open bugs..."
    OPEN_BUGS=$(gh issue list --repo $REPO --label bug --state open --json number --jq '. | length')

    if [ "$OPEN_BUGS" -eq 0 ]; then
        echo "✅ No open bugs! Loop complete."
        break
    fi

    echo "Found $OPEN_BUGS open bug(s)"

    # Get the newest auto-reported bug
    BUG_NUMBER=$(gh issue list --repo $REPO --label "auto-reported" --state open --json number --jq '.[0].number')

    if [ -z "$BUG_NUMBER" ]; then
        # Fallback to any bug
        BUG_NUMBER=$(gh issue list --repo $REPO --label bug --state open --json number --jq '.[0].number')
    fi

    if [ -z "$BUG_NUMBER" ]; then
        echo "⚠️  Could not get bug number. Stopping."
        break
    fi

    echo "🐛 Working on bug #$BUG_NUMBER"

    # Get bug details
    gh issue view $BUG_NUMBER --repo $REPO

    echo ""
    echo "📝 Prompting Claude Code to fix this bug..."
    echo ""
    echo "Waiting for Claude Code to:"
    echo "  1. Analyze bug #$BUG_NUMBER"
    echo "  2. Download action log from gist (if available)"
    echo "  3. Write failing test"
    echo "  4. Implement fix"
    echo "  5. Run all tests"
    echo "  6. Commit changes"
    echo ""
    echo "Press ENTER when Claude Code completes this bug, or Ctrl+C to stop..."
    read -r

    # Verify tests pass
    echo ""
    echo "🧪 Running full test suite..."
    if python -m pytest -m "not integration" -v; then
        echo "✅ All tests passed!"
    else
        echo "❌ Tests failed. Please fix before continuing."
        echo "Press ENTER to skip this bug and continue, or Ctrl+C to stop..."
        read -r
    fi

    echo "Iteration $ITERATION complete ✅"
done

echo ""
echo "🎉 Autonomous Development Loop Complete!"
echo "Total iterations: $ITERATION"
echo ""
echo "Summary:"
gh issue list --repo $REPO --label bug --state open
