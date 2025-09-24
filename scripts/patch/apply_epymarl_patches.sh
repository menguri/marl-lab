#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PATCH_DIR="$ROOT_DIR/patches/epymarl"
SUBMODULE_DIR="$ROOT_DIR/external/epymarl"

if [[ ! -d "$PATCH_DIR" ]]; then
  echo "No epymarl patches found (expected directory: $PATCH_DIR)."
  exit 0
fi

if [[ ! -e "$SUBMODULE_DIR/.git" ]]; then
  echo "epymarl submodule not initialized at $SUBMODULE_DIR." >&2
  exit 1
fi

shopt -s nullglob
patches=("$PATCH_DIR"/*.patch)

if [[ ${#patches[@]} -eq 0 ]]; then
  echo "No patch files in $PATCH_DIR."
  exit 0
fi

for patch in "${patches[@]}"; do
  patch_name=$(basename "$patch")
  if git -C "$SUBMODULE_DIR" apply --check "$patch" >/dev/null 2>&1; then
    echo "Applying $patch_name"
    git -C "$SUBMODULE_DIR" apply "$patch"
  elif git -C "$SUBMODULE_DIR" apply --check --reverse "$patch" >/dev/null 2>&1; then
    echo "Skipping $patch_name (already applied)"
  else
    echo "Failed to apply $patch_name" >&2
    exit 1
  fi
done
