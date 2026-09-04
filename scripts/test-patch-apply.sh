#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-NuvioDesktop}"

echo "==> [1/4] Resetting $TARGET_DIR to clean HEAD..."
git -C "$TARGET_DIR" reset --hard HEAD
git -C "$TARGET_DIR" clean -fd

PATCHES=(
    "patches/01-branding-side-by-side.patch"
    "patches/02-app-updater.patch"
    "patches/03-live-tv.patch"
)

for patch in "${PATCHES[@]}"; do
    if [[ ! -f "$patch" ]]; then
        echo "Error: Patch file not found: $patch" >&2
        exit 1
    fi
    echo "==> Applying $patch..."
    git -C "$TARGET_DIR" apply --ignore-space-change --3way "$patch"
done

echo "==> [4/4] All patches applied successfully!"
git -C "$TARGET_DIR" status --short
