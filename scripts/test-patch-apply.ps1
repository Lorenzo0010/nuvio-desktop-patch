param(
    [string]$TargetDir = "NuvioDesktop"
)

$ErrorActionPreference = "Stop"

Write-Host "==> [1/4] Resetting $TargetDir to clean HEAD..." -ForegroundColor Cyan
git -C $TargetDir reset --hard HEAD
git -C $TargetDir clean -fd

$patches = @(
    "patches/01-branding-side-by-side.patch",
    "patches/02-app-updater.patch",
    "patches/03-live-tv.patch"
)

foreach ($patch in $patches) {
    if (-not (Test-Path $patch)) {
        Write-Error "Patch file not found: $patch"
    }
    Write-Host "==> Applying $patch..." -ForegroundColor Cyan
    git -C $TargetDir apply --3way (Resolve-Path $patch).Path
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to apply $patch"
    }
}

Write-Host "==> [4/4] All patches applied successfully!" -ForegroundColor Green
git -C $TargetDir status --short
