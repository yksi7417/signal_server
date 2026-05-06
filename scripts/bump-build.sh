#!/bin/bash
# Increments BUILD_NUMBER in Project.env. TestFlight rejects duplicate
# build numbers for the same MARKETING_VERSION, so call this before every
# archive that's going to be uploaded.
#
# Usage: ./scripts/bump-build.sh             # bumps by 1
#        ./scripts/bump-build.sh --to 42     # set to a specific number
set -euo pipefail

ENV_FILE="$(dirname "$0")/../Project.env"
ENV_FILE="$(cd "$(dirname "$ENV_FILE")" && pwd)/$(basename "$ENV_FILE")"

if [ ! -f "$ENV_FILE" ]; then
  echo "✗ $ENV_FILE not found"
  exit 1
fi

current=$(grep '^BUILD_NUMBER=' "$ENV_FILE" | cut -d= -f2)
if [ -z "$current" ]; then current=0; fi

case "${1:-}" in
  --to)
    next="${2:-}"
    if ! [[ "$next" =~ ^[0-9]+$ ]]; then
      echo "✗ --to requires a positive integer"
      exit 1
    fi
    ;;
  *)
    next=$((current + 1))
    ;;
esac

# Cross-platform sed -i (BSD vs GNU): write to tmp + mv to avoid the in-place flag.
tmp=$(mktemp)
sed "s/^BUILD_NUMBER=.*/BUILD_NUMBER=$next/" "$ENV_FILE" > "$tmp"
mv "$tmp" "$ENV_FILE"

echo "BUILD_NUMBER: $current → $next"
