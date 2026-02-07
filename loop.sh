#!/bin/bash

# Ralph Wiggum Loop for OpenCode
# Usage: ./loop.sh [mode] [max_iterations]
#   mode: build (default) or plan
#   max_iterations: optional limit (default: infinite)

set -euo pipefail

MODE="${1:-build}"
MAX_ITERATIONS="${2:-0}"
ITERATION=0

PROMPT_FILE="PROMPT_${MODE}.md"

if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Error: $PROMPT_FILE not found"
    exit 1
fi

# Read the prompt file content
PROMPT_CONTENT=$(cat "$PROMPT_FILE")

# Use Kimi K2.5 Free model (current model being used)
MODEL=opencode/kimi-k2.5-free

echo "Ralph Wiggum AI Agent - Mode: $MODE"
echo "========================================"
echo "Model: $MODEL"
echo ""

if [[ $MAX_ITERATIONS -gt 0 ]]; then
    echo "Max iterations: $MAX_ITERATIONS"
else
    echo "Running until interrupted (Ctrl+C to stop)"
fi

echo ""
echo "Press Enter to start Ralph (or Ctrl+C to cancel)..."
read -r

while true; do
    ITERATION=$((ITERATION + 1))
    
    echo ""
    echo "--------------------------------------------"
    echo "Iteration $ITERATION - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "--------------------------------------------"
    echo ""
    
    # Run opencode non-interactively with the prompt
    # Uses 'opencode run' which executes and exits after completion
    opencode run \
        -m "$MODEL" \
        --title "Ralph ${MODE} iteration ${ITERATION}" \
        "$PROMPT_CONTENT" || {
        echo ""
        echo "OpenCode exited with error (code: $?). Continuing to next iteration..."
        echo ""
    }
    
    echo ""
    echo "Iteration $ITERATION complete"
    
    # Push changes to remote after each iteration
    echo "Pushing changes to remote..."
    git push origin main || {
        echo "Warning: git push failed (code: $?). Continuing..."
    }
    
    # Check if we've reached max iterations
    if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
        echo ""
        echo "Reached maximum iterations ($MAX_ITERATIONS). Stopping."
        break
    fi
    
    # Small delay between iterations to avoid hammering
    sleep 2
done

echo ""
echo "Ralph is done!"
