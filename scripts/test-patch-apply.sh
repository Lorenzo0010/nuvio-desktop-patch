#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-NuvioDesktop}"

BASE_COMMIT="origin/Dev"
if [[ -f ".last_built_upstream_sha" ]]; then
    SHA=$(cat .last_built_upstream_sha | tr -d '\r\n[:space:]')
    if [[ -n "$SHA" ]]; then
        BASE_COMMIT="$SHA"
    fi
fi

echo "==> [1/4] Resetting $TARGET_DIR to clean upstream ($BASE_COMMIT)..."
git -C "$TARGET_DIR" checkout Dev
git -C "$TARGET_DIR" reset --hard "$BASE_COMMIT"
git -C "$TARGET_DIR" clean -fd

PATCHES=(
    "patches/01-branding-side-by-side.patch"
    "patches/02-app-updater.patch"
    "patches/03-live-tv.patch"
    "patches/04-hls-downloads.patch"
    "patches/05-desktop-plugins-fix.patch"
    "patches/06-stream-prefetch.patch"
    "patches/07-version-bump.patch"
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
mkdir -p "$TARGET_DIR/composeApp/build/native/windows" "$TARGET_DIR/composeApp/src/desktopMain/native/windows/runtime"
cp -f "assets/native/windows/player_bridge.dll" "$TARGET_DIR/composeApp/build/native/windows/player_bridge.dll" 2>/dev/null || true
cp -f "assets/native/windows/WebView2Loader.dll" "$TARGET_DIR/composeApp/src/desktopMain/native/windows/runtime/WebView2Loader.dll" 2>/dev/null || true
[[ -f "$TARGET_DIR/local.properties" ]] || touch "$TARGET_DIR/local.properties"

git -C "$TARGET_DIR" status --short
