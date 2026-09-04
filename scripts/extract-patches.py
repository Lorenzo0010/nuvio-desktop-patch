import subprocess
import os

repo_dir = r"F:\GitHub\nuviodesktop\NuvioDesktop"
patches_dir = r"F:\GitHub\nuviodesktop\patches"
os.makedirs(patches_dir, exist_ok=True)

patch_01_files = [
    "composeApp/build.gradle.kts",
    "composeApp/src/desktopMain/kotlin/com/nuvio/app/Main.kt",
    "composeApp/src/desktopMain/kotlin/com/nuvio/app/core/storage/DesktopStorage.kt",
]

patch_02_files = [
    "composeApp/src/desktopMain/kotlin/com/nuvio/app/features/updater/AppUpdaterPlatform.desktop.kt",
]

patch_03_files = [
    "composeApp/src/androidMain/kotlin/com/nuvio/app/MainActivity.kt",
    "composeApp/src/commonMain/composeResources/values/strings.xml",
    "composeApp/src/commonMain/composeResources/values-it/strings.xml",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/AppScreenTab.kt",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/AppShellComponents.kt",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/MainAppContent.kt",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/MainTabsDestination.kt",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/PlayerControls.kt",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/PlayerScreenRuntimeState.kt",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/PlayerScreenRuntimeUi.kt",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/LiveTvChannelsPanel.kt",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/LiveTvPlayerActions.kt",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/features/livetv",
    "composeApp/src/desktopMain/kotlin/com/nuvio/app/features/livetv",
    "composeApp/src/androidMain/kotlin/com/nuvio/app/features/livetv",
    "composeApp/src/iosMain/kotlin/com/nuvio/app/features/livetv",
]

def export_patch(filename, files):
    out_path = os.path.join(patches_dir, filename)
    cmd = ["git", "-C", repo_dir, "diff", "HEAD", "--"] + files
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    if result.returncode != 0:
        print(f"Error extracting {filename}: {result.stderr}")
        return
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(result.stdout)
    print(f"Successfully exported {filename} ({len(result.stdout)} bytes)")

# Ensure intent-to-add for untracked files in patch 03
untracked_dirs = [
    "composeApp/src/commonMain/kotlin/com/nuvio/app/features/livetv",
    "composeApp/src/desktopMain/kotlin/com/nuvio/app/features/livetv",
    "composeApp/src/androidMain/kotlin/com/nuvio/app/features/livetv",
    "composeApp/src/iosMain/kotlin/com/nuvio/app/features/livetv",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/LiveTvChannelsPanel.kt",
    "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/LiveTvPlayerActions.kt",
]
for p in untracked_dirs:
    subprocess.run(["git", "-C", repo_dir, "add", "-N", p], check=False)

export_patch("01-branding-side-by-side.patch", patch_01_files)
export_patch("02-app-updater.patch", patch_02_files)
export_patch("03-live-tv.patch", patch_03_files)
