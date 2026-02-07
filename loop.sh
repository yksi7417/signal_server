#!/bin/bash

# Ralph Wiggum Loop for Claude Code
# Usage: ./loop.sh [mode] [max_iterations] [max_turns]
#   mode: build (default) or plan
#   max_iterations: optional limit on loop iterations (default: infinite)
#   max_turns: optional limit on agentic turns per iteration (default: 50)

set -euo pipefail

MODE="${1:-build}"
MAX_ITERATIONS="${2:-0}"
MAX_TURNS="${3:-50}"
ITERATION=0

PROMPT_FILE="PROMPT_${MODE}.md"

if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Error: $PROMPT_FILE not found"
    exit 1
fi

# Read the prompt file content
PROMPT_CONTENT=$(cat "$PROMPT_FILE")

# Get the current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Ralph Wiggum AI Agent - Mode: $MODE"
echo "========================================"
echo "Tool: Claude Code (claude -p)"
echo "Branch: $CURRENT_BRANCH"
echo "Max turns per iteration: $MAX_TURNS"
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
    echo "============================================"
    echo "Iteration $ITERATION - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================"
    echo ""

    # Run claude in non-interactive print mode (-p) with:
    #   --dangerously-skip-permissions: no interactive permission prompts
    #   --max-turns: limit agentic turns to keep context in the "good zone"
    #   --verbose: show tool usage for observability
    claude -p \
        --dangerously-skip-permissions \
        --max-turns "$MAX_TURNS" \
        --verbose \
        "$PROMPT_CONTENT" || {
        EXIT_CODE=$?
        echo ""
        echo "Claude exited with code $EXIT_CODE. Continuing to next iteration..."
        echo ""
    }

    echo ""
    echo "Iteration $ITERATION complete at $(date '+%Y-%m-%d %H:%M:%S')"

    # Push changes to remote after each iteration
    echo "Pushing changes to remote..."
    git push origin "$CURRENT_BRANCH" || {
        echo "Warning: git push failed. Continuing..."
    }

    # Check if we've reached max iterations
    if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
        echo ""
        echo "Reached maximum iterations ($MAX_ITERATIONS). Stopping."
        break
    fi

    # Small delay between iterations
    sleep 5
done

echo ""
echo "Ralph is done! Completed $ITERATION iterations."
