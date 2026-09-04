param(
    [string]$TargetDir = "NuvioDesktop"
)

$ErrorActionPreference = "Stop"

Write-Host "==> [1/4] Resetting $TargetDir to clean upstream Dev..." -ForegroundColor Cyan
git -C $TargetDir checkout Dev
git -C $TargetDir reset --hard origin/Dev
git -C $TargetDir clean -fd

$patches = @(
    "patches/01-branding-side-by-side.patch",
    "patches/02-app-updater.patch",
    "patches/03-live-tv.patch",
    "patches/04-hls-downloads.patch"
)

foreach ($patch in $patches) {
    if (-not (Test-Path $patch)) {
        Write-Error "Patch file not found: $patch"
    }
    Write-Host "==> Applying $patch..." -ForegroundColor Cyan
    git -C $TargetDir apply --ignore-space-change --3way (Resolve-Path $patch).Path
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to apply $patch"
    }
}

Write-Host "==> [4/4] All patches applied successfully!" -ForegroundColor Green

Write-Host "==> Ensuring native binaries from assets/native/windows..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "$TargetDir\composeApp\build\native\windows" -Force | Out-Null
New-Item -ItemType Directory -Path "$TargetDir\composeApp\src\desktopMain\native\windows\runtime" -Force | Out-Null
Copy-Item "assets\native\windows\player_bridge.dll" "$TargetDir\composeApp\build\native\windows\player_bridge.dll" -Force
Copy-Item "assets\native\windows\WebView2Loader.dll" "$TargetDir\composeApp\src\desktopMain\native\windows\runtime\WebView2Loader.dll" -Force

git -C $TargetDir status --short

