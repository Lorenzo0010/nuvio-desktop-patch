import os
import shutil
import subprocess
import tempfile

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
repo_dir = os.path.join(root_dir, "NuvioDesktop")
patches_dir = os.path.join(root_dir, "patches")
os.makedirs(patches_dir, exist_ok=True)

def run(cmd, cwd=repo_dir, check=True):
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if check and res.returncode != 0:
        print(f"FAILED: {' '.join(cmd)}")
        print(res.stderr)
        raise RuntimeError(res.stderr)
    return res

print("==> Backing up current NuvioDesktop worktree...")
temp_dir = tempfile.mkdtemp(prefix="nuvio_patch_backup_")

status_res = run(["git", "status", "--porcelain"])
for line in status_res.stdout.splitlines():
    path = line[3:].strip()
    if path.endswith(".dll") or path.endswith(".jar") or path.endswith(".aar"):
        continue
    sp = os.path.join(repo_dir, path)
    if os.path.isfile(sp):
        dp = os.path.join(temp_dir, path)
        os.makedirs(os.path.dirname(dp), exist_ok=True)
        shutil.copy2(sp, dp)
    elif os.path.isdir(sp):
        for r, _, fnames in os.walk(sp):
            for fn in fnames:
                if fn.endswith(".dll") or fn.endswith(".jar") or fn.endswith(".aar"):
                    continue
                fpath = os.path.join(r, fn)
                rel = os.path.relpath(fpath, repo_dir)
                dp = os.path.join(temp_dir, rel)
                os.makedirs(os.path.dirname(dp), exist_ok=True)
                shutil.copy2(fpath, dp)

try:
    print("==> Switching NuvioDesktop to temporary builder branch...")
    run(["git", "checkout", "-B", "patch-builder"])
    run(["git", "reset", "--hard", "origin/Dev"])
    run(["git", "clean", "-fd"])

    # Patch 01
    print("==> Preparing Patch 01: Branding Side-by-Side...")
    p1_files = [
        "composeApp/build.gradle.kts",
        "composeApp/src/desktopMain/kotlin/com/nuvio/app/Main.kt",
        "composeApp/src/desktopMain/kotlin/com/nuvio/app/core/storage/DesktopStorage.kt",
        "composeApp/src/desktopMain/kotlin/com/nuvio/app/features/player/desktop/NativePlayerBridge.kt",
    ]
    for f in p1_files:
        shutil.copy2(os.path.join(temp_dir, f), os.path.join(repo_dir, f))
    run(["git", "add"] + p1_files)
    run(["git", "commit", "-m", "Patch 01: Branding Side-by-Side"])

    # Patch 02
    print("==> Preparing Patch 02: App Updater...")
    p2_files = [
        "composeApp/src/desktopMain/kotlin/com/nuvio/app/features/updater/AppUpdaterPlatform.desktop.kt",
    ]
    for f in p2_files:
        shutil.copy2(os.path.join(temp_dir, f), os.path.join(repo_dir, f))
    run(["git", "add"] + p2_files)
    run(["git", "commit", "-m", "Patch 02: App Updater"])

    # Patch 03
    print("==> Preparing Patch 03: Live TV...")
    p3_dirs = [
        "composeApp/src/commonMain/kotlin/com/nuvio/app/features/livetv",
        "composeApp/src/desktopMain/kotlin/com/nuvio/app/features/livetv",
        "composeApp/src/androidMain/kotlin/com/nuvio/app/features/livetv",
        "composeApp/src/iosMain/kotlin/com/nuvio/app/features/livetv",
    ]
    for d in p3_dirs:
        sd = os.path.join(temp_dir, d)
        dd = os.path.join(repo_dir, d)
        if os.path.exists(dd):
            shutil.rmtree(dd)
        shutil.copytree(sd, dd)

    p3_standalone = [
        "composeApp/src/androidMain/kotlin/com/nuvio/app/MainActivity.kt",
        "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/PlayerControls.kt",
        "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/PlayerScreenRuntimeState.kt",
        "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/PlayerScreenRuntimeUi.kt",
        "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/LiveTvChannelsPanel.kt",
        "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/LiveTvPlayerActions.kt",
    ]
    for f in p3_standalone:
        df = os.path.join(repo_dir, f)
        os.makedirs(os.path.dirname(df), exist_ok=True)
        shutil.copy2(os.path.join(temp_dir, f), df)

    # Copy LiveTv strings to strings.xml
    LIVETV_STRINGS_EN = '''
    <string name="live_tv_title">Live TV</string>
    <string name="live_tv_channel_group_default">Channel</string>
    <string name="live_tv_empty_title">No channels found</string>
    <string name="live_tv_empty_message">Check your playlist URL or try refreshing it.</string>
    <string name="live_tv_load_failed">Playlist could not be loaded</string>
    <string name="live_tv_no_playlist_title">No playlist configured</string>
    <string name="live_tv_no_playlist_message">Add an M3U playlist to list channels here.</string>
    <string name="live_tv_settings_section_playlist">PLAYLIST</string>
    <string name="live_tv_settings_playlist_label">M3U playlist URL</string>
    <string name="live_tv_settings_playlist_placeholder">https://example.com/playlist.m3u8</string>
    <string name="live_tv_settings_description">Channels from this playlist will appear in the Live TV tab.</string>
    <string name="live_tv_search_placeholder">Search channels...</string>
    <string name="live_tv_link_copied">Link copied</string>
    <string name="live_tv_add_source">Add source</string>
    <string name="live_tv_all_channels">All channels</string>
    <string name="live_tv_channel_count">%1$d channels</string>
    <string name="live_tv_channels">Channels</string>
    <string name="live_tv_disconnect">Disconnect</string>
    <string name="live_tv_empty_description">Enter an M3U playlist URL to start watching live TV channels.</string>
    <string name="live_tv_favorite">Favorite</string>
    <string name="live_tv_favorites">Favorites</string>
    <string name="live_tv_load">Load</string>
    <string name="live_tv_no_channels_found">No channels found</string>
    <string name="live_tv_no_favorites">No favorite channels yet</string>
    <string name="live_tv_player_channels">Channels</string>
    <string name="live_tv_recent_channel_cta">Play</string>
    <string name="live_tv_recent_channel_title">Recent channel</string>
    <string name="live_tv_refresh">Refresh</string>
    <string name="live_tv_search">Search</string>
    <string name="live_tv_choose_category">Choose category</string>
    <string name="live_tv_source_hint">https://example.com/playlist.m3u</string>
    <string name="live_tv_source_title">Source URL</string>
    <string name="live_tv_categories">Categories</string>
    <string name="live_tv_open_channels">Channels</string>
    <string name="compose_player_channels">Channels</string>
'''
    LIVETV_STRINGS_IT = '''
    <string name="live_tv_title">Live TV</string>
    <string name="live_tv_channel_group_default">Canale</string>
    <string name="live_tv_empty_title">Nessun canale trovato</string>
    <string name="live_tv_empty_message">Controlla l\\'URL della tua playlist o prova ad aggiornarla.</string>
    <string name="live_tv_load_failed">Impossibile caricare la playlist</string>
    <string name="live_tv_no_playlist_title">Nessuna playlist configurata</string>
    <string name="live_tv_no_playlist_message">Aggiungi una playlist M3U per visualizzare i canali qui.</string>
    <string name="live_tv_settings_section_playlist">PLAYLIST</string>
    <string name="live_tv_settings_playlist_label">URL playlist M3U</string>
    <string name="live_tv_settings_playlist_placeholder">https://example.com/playlist.m3u8</string>
    <string name="live_tv_settings_description">I canali di questa playlist appariranno nella scheda Live TV.</string>
    <string name="live_tv_search_placeholder">Cerca canali...</string>
    <string name="live_tv_link_copied">Link copiato</string>
    <string name="live_tv_add_source">Aggiungi sorgente</string>
    <string name="live_tv_all_channels">Tutti i canali</string>
    <string name="live_tv_channel_count">%1$d canali</string>
    <string name="live_tv_channels">Canali</string>
    <string name="live_tv_disconnect">Disconnetti</string>
    <string name="live_tv_empty_description">Inserisci l\\'URL di una playlist M3U per iniziare a guardare i canali in diretta.</string>
    <string name="live_tv_favorite">Preferito</string>
    <string name="live_tv_favorites">Preferiti</string>
    <string name="live_tv_load">Carica</string>
    <string name="live_tv_no_channels_found">Nessun canale trovato</string>
    <string name="live_tv_no_favorites">Nessun canale preferito</string>
    <string name="live_tv_player_channels">Canali</string>
    <string name="live_tv_recent_channel_cta">Riproduci</string>
    <string name="live_tv_recent_channel_title">Canale recente</string>
    <string name="live_tv_refresh">Aggiorna</string>
    <string name="live_tv_search">Cerca</string>
    <string name="live_tv_choose_category">Scegli categoria</string>
    <string name="live_tv_source_hint">https://example.com/playlist.m3u</string>
    <string name="live_tv_source_title">URL Sorgente</string>
    <string name="live_tv_categories">Categorie</string>
    <string name="live_tv_open_channels">Canali</string>
    <string name="compose_player_channels">Canali</string>
'''
    fp_en = os.path.join(repo_dir, "composeApp/src/commonMain/composeResources/values/strings.xml")
    with open(fp_en, "r", encoding="utf-8") as f:
        c_en = f.read().replace("</resources>", LIVETV_STRINGS_EN.strip("\n") + "\n</resources>")
    with open(fp_en, "w", encoding="utf-8", newline="\n") as f:
        f.write(c_en)

    fp_it = os.path.join(repo_dir, "composeApp/src/commonMain/composeResources/values-it/strings.xml")
    with open(fp_it, "r", encoding="utf-8") as f:
        c_it = f.read().replace("</resources>", LIVETV_STRINGS_IT.strip("\n") + "\n</resources>")
    with open(fp_it, "w", encoding="utf-8", newline="\n") as f:
        f.write(c_it)

    # AppScreenTab.kt with LiveTv
    app_screen_tab_p3 = '''package com.nuvio.app

import com.nuvio.app.core.ui.NativeNavigationTab

enum class AppScreenTab {
    Home,
    Search,
    LiveTv,
    Library,
    Settings,
    ;

    companion object {
        fun fromName(name: String): AppScreenTab =
            entries.firstOrNull { it.name.equals(name, ignoreCase = true) } ?: Home
    }
}

internal fun AppScreenTab.toNativeNavigationTab(): NativeNavigationTab = when (this) {
    AppScreenTab.Home -> NativeNavigationTab.Home
    AppScreenTab.Search -> NativeNavigationTab.Search
    AppScreenTab.LiveTv -> NativeNavigationTab.Home
    AppScreenTab.Library -> NativeNavigationTab.Library
    AppScreenTab.Settings -> NativeNavigationTab.Settings
}

internal fun NativeNavigationTab.toAppScreenTab(): AppScreenTab = when (this) {
    NativeNavigationTab.Home -> AppScreenTab.Home
    NativeNavigationTab.Search -> AppScreenTab.Search
    NativeNavigationTab.Library -> AppScreenTab.Library
    NativeNavigationTab.Settings -> AppScreenTab.Settings
}
'''
    with open(os.path.join(repo_dir, "composeApp/src/commonMain/kotlin/com/nuvio/app/AppScreenTab.kt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(app_screen_tab_p3)

    # MainTabsDestination.kt with LiveTv
    fp_mtd = os.path.join(repo_dir, "composeApp/src/commonMain/kotlin/com/nuvio/app/MainTabsDestination.kt")
    with open(fp_mtd, "r", encoding="utf-8") as f:
        mtd = f.read()
    mtd = mtd.replace('import com.nuvio.app.features.settings.NavBarStyle',
'''import com.nuvio.app.features.settings.NavBarStyle
import androidx.compose.material.icons.rounded.Tv
import nuvio.composeapp.generated.resources.live_tv_title''')
    mtd = mtd.replace(
'''                        NavItem(
                            selected = selectedTab == AppScreenTab.Search,
                            onClick = { onTabSelected(AppScreenTab.Search) },
                            icon = Res.drawable.sidebar_search,
                            contentDescription = stringResource(Res.string.compose_nav_search),
                        )
                        NavItem(
                            selected = selectedTab == AppScreenTab.Library,''',
'''                        NavItem(
                            selected = selectedTab == AppScreenTab.Search,
                            onClick = { onTabSelected(AppScreenTab.Search) },
                            icon = Res.drawable.sidebar_search,
                            contentDescription = stringResource(Res.string.compose_nav_search),
                        )
                        NavItem(
                            selected = selectedTab == AppScreenTab.LiveTv,
                            onClick = { onTabSelected(AppScreenTab.LiveTv) },
                            icon = Icons.Rounded.Tv,
                            contentDescription = stringResource(Res.string.live_tv_title),
                        )
                        NavItem(
                            selected = selectedTab == AppScreenTab.Library,'''
    )
    mtd = mtd.replace(
'''                        NavItem(
                            selected = selectedTab == AppScreenTab.Search,
                            onClick = { onTabSelected(AppScreenTab.Search) },
                            icon = Res.drawable.sidebar_search,
                            contentDescription = stringResource(Res.string.compose_nav_search),
                            label = stringResource(Res.string.compose_nav_search),
                        )
                        NavItem(
                            selected = selectedTab == AppScreenTab.Library,''',
'''                        NavItem(
                            selected = selectedTab == AppScreenTab.Search,
                            onClick = { onTabSelected(AppScreenTab.Search) },
                            icon = Res.drawable.sidebar_search,
                            contentDescription = stringResource(Res.string.compose_nav_search),
                            label = stringResource(Res.string.compose_nav_search),
                        )
                        NavItem(
                            selected = selectedTab == AppScreenTab.LiveTv,
                            onClick = { onTabSelected(AppScreenTab.LiveTv) },
                            icon = Icons.Rounded.Tv,
                            contentDescription = stringResource(Res.string.live_tv_title),
                            label = stringResource(Res.string.live_tv_title),
                        )
                        NavItem(
                            selected = selectedTab == AppScreenTab.Library,'''
    )
    with open(fp_mtd, "w", encoding="utf-8", newline="\n") as f:
        f.write(mtd)

    # AppShellComponents.kt with LiveTv
    fp_asc = os.path.join(repo_dir, "composeApp/src/commonMain/kotlin/com/nuvio/app/AppShellComponents.kt")
    with open(fp_asc, "r", encoding="utf-8") as f:
        asc = f.read()
    asc = asc.replace('import com.nuvio.app.features.home.HomeCatalogSection',
'''import com.nuvio.app.features.home.HomeCatalogSection
import com.nuvio.app.features.livetv.LiveTvChannel
import com.nuvio.app.features.livetv.LiveTvScreen
import androidx.compose.material.icons.rounded.Tv
import nuvio.composeapp.generated.resources.live_tv_title''')
    asc = asc.replace(
'''internal data class AppTabRequests(
    val homeScrollToTopRequests: Flow<Unit>,
    val searchScrollToTopRequests: Flow<Unit>,
    val libraryScrollToTopRequests: Flow<Unit>,
    val settingsRootActionRequests: Flow<Unit>,
)''',
'''internal data class AppTabRequests(
    val homeScrollToTopRequests: Flow<Unit>,
    val searchScrollToTopRequests: Flow<Unit>,
    val liveTvScrollToTopRequests: Flow<Unit> = emptyFlow(),
    val libraryScrollToTopRequests: Flow<Unit>,
    val settingsRootActionRequests: Flow<Unit>,
)''')
    asc = asc.replace(
'''    val onFolderClick: ((collectionId: String, folderId: String) -> Unit)? = null,
    val onRequestedSettingsPageConsumed: () -> Unit = {},
    val onInitialHomeContentRendered: () -> Unit = {},
)''',
'''    val onFolderClick: ((collectionId: String, folderId: String) -> Unit)? = null,
    val onRequestedSettingsPageConsumed: () -> Unit = {},
    val onInitialHomeContentRendered: () -> Unit = {},
    val onLiveTvChannelClick: ((LiveTvChannel) -> Unit)? = null,
)''')
    asc = asc.replace(
'''                    when (selectedTab) {
                        AppScreenTab.Home -> Unit

                        AppScreenTab.Search -> {''',
'''                    when (selectedTab) {
                        AppScreenTab.Home -> Unit

                        AppScreenTab.LiveTv -> {
                            LiveTvScreen(
                                modifier = Modifier.fillMaxSize(),
                                scrollToTopRequests = requests.liveTvScrollToTopRequests,
                                onChannelClick = { channel -> actions.onLiveTvChannelClick?.invoke(channel) },
                            )
                        }

                        AppScreenTab.Search -> {''')
    tablet_livetv_pill = '''                    TabletTopPillItem(
                        label = stringResource(Res.string.live_tv_title),
                        selected = selectedTab == AppScreenTab.LiveTv,
                        onClick = { onTabSelected(AppScreenTab.LiveTv) },
                        labelFraction = labelFraction,
                        pillHeight = pillHeight,
                        expandedHorizontalPadding = expandedHorizontalPadding,
                        collapsedHorizontalPadding = iconCollapsedPadding,
                        textStyle = labelTextStyle,
                        icon = {
                            Icon(
                                imageVector = Icons.Rounded.Tv,
                                contentDescription = stringResource(Res.string.live_tv_title),
                                modifier = Modifier.size(navIconSize),
                                tint = if (selectedTab == AppScreenTab.LiveTv) {
                                    tokens.colors.textPrimary
                                } else {
                                    Color.White.copy(alpha = 0.70f)
                                },
                            )
                        },
                    )
                    TabletTopPillItem(
                        label = stringResource(Res.string.compose_nav_library),'''
    asc = asc.replace('''                    TabletTopPillItem(
                        label = stringResource(Res.string.compose_nav_library),''', tablet_livetv_pill)

    desktop_livetv_item = '''                DesktopSidebarItem(
                    label = stringResource(Res.string.live_tv_title),
                    selected = selectedTab == AppScreenTab.LiveTv,
                    expanded = sidebarExpanded,
                    onClick = { selectTab(AppScreenTab.LiveTv) },
                ) { color ->
                    Icon(
                        imageVector = Icons.Rounded.Tv,
                        contentDescription = stringResource(Res.string.live_tv_title),
                        modifier = Modifier.size(DesktopSidebarIconSize),
                        tint = color,
                    )
                }
                DesktopSidebarItem(
                    label = stringResource(Res.string.compose_nav_library),'''
    asc = asc.replace('''                DesktopSidebarItem(
                    label = stringResource(Res.string.compose_nav_library),''', desktop_livetv_item)

    with open(fp_asc, "w", encoding="utf-8", newline="\n") as f:
        f.write(asc)

    # MainAppContent.kt with LiveTv
    fp_mac = os.path.join(repo_dir, "composeApp/src/commonMain/kotlin/com/nuvio/app/MainAppContent.kt")
    with open(fp_mac, "r", encoding="utf-8") as f:
        mac = f.read()
    mac = mac.replace('import com.nuvio.app.features.home.HomeScreen',
'''import com.nuvio.app.features.home.HomeScreen
import com.nuvio.app.features.livetv.LiveTvChannel
import com.nuvio.app.features.livetv.LiveTvRepository''')
    mac = mac.replace('val searchScrollToTopRequests = remember { MutableSharedFlow<Unit>(extraBufferCapacity = 1) }',
'''val searchScrollToTopRequests = remember { MutableSharedFlow<Unit>(extraBufferCapacity = 1) }
    val liveTvScrollToTopRequests = remember { MutableSharedFlow<Unit>(extraBufferCapacity = 1) }''')
    mac = mac.replace(
'''            AppScreenTab.Search -> {
                searchFocusRequestCount++
                searchScrollToTopRequests.tryEmit(Unit)
            }
            AppScreenTab.Library -> libraryScrollToTopRequests.tryEmit(Unit)''',
'''            AppScreenTab.Search -> {
                searchFocusRequestCount++
                searchScrollToTopRequests.tryEmit(Unit)
            }
            AppScreenTab.LiveTv -> liveTvScrollToTopRequests.tryEmit(Unit)
            AppScreenTab.Library -> libraryScrollToTopRequests.tryEmit(Unit)''')
    mac = mac.replace(
'''                        requests = AppTabRequests(
                            homeScrollToTopRequests = homeScrollToTopRequests,
                            searchScrollToTopRequests = searchScrollToTopRequests,
                            libraryScrollToTopRequests = libraryScrollToTopRequests,
                            settingsRootActionRequests = settingsRootActionRequests,
                        ),''',
'''                        requests = AppTabRequests(
                            homeScrollToTopRequests = homeScrollToTopRequests,
                            searchScrollToTopRequests = searchScrollToTopRequests,
                            liveTvScrollToTopRequests = liveTvScrollToTopRequests,
                            libraryScrollToTopRequests = libraryScrollToTopRequests,
                            settingsRootActionRequests = settingsRootActionRequests,
                        ),''')
    mac = mac.replace(
'''                                onRequestedSettingsPageConsumed = {
                                    requestedSettingsPageName = null
                                },
                                onInitialHomeContentRendered = { initialHomeReady = true },
                            )''',
'''                                onLiveTvChannelClick = ::openLiveTvChannel,
                                onRequestedSettingsPageConsumed = {
                                    requestedSettingsPageName = null
                                },
                                onInitialHomeContentRendered = { initialHomeReady = true },
                            )''')
    open_livetv_fn = '''        fun openLiveTvChannel(channel: LiveTvChannel) {
            LiveTvRepository.recordRecentChannel(channel)
            val playerLaunch = PlayerLaunch(
                profileId = activePlaybackProfileId,
                title = channel.name,
                sourceUrl = channel.streamUrl,
                sourceHeaders = channel.headers,
                logo = channel.logoUrl,
                streamTitle = channel.name,
                streamSubtitle = channel.group,
                providerName = "Live TV",
                providerAddonId = "live-tv",
                contentType = "live",
                videoId = channel.id,
                parentMetaId = channel.id,
                parentMetaType = "live",
            )
            if (playerSettingsUiState.externalPlayerEnabled) {
                coroutineScope.launch { openExternalPlayback(playerLaunch) }
                return
            }
            val launchId = PlayerLaunchStore.put(playerLaunch)
            navController.navigate(PlayerRoute(launchId = launchId, title = playerLaunch.title))
        }

        fun openExternalStreamUrl(url: String): Boolean {'''
    mac = mac.replace('        fun openExternalStreamUrl(url: String): Boolean {', open_livetv_fn)
    with open(fp_mac, "w", encoding="utf-8", newline="\n") as f:
        f.write(mac)

    run(["git", "add", "-A"])
    run(["git", "commit", "-m", "Patch 03: Live TV"])

    # Patch 04
    print("==> Preparing Patch 04: HLS Downloads...")
    for root, _, fnames in os.walk(temp_dir):
        for fn in fnames:
            if fn.endswith(".dll") or fn.endswith(".jar") or fn.endswith(".aar"):
                continue
            sp = os.path.join(root, fn)
            rel = os.path.relpath(sp, temp_dir)
            dp = os.path.join(repo_dir, rel)
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            shutil.copy2(sp, dp)

    run(["git", "add", "-A"])
    run(["git", "commit", "-m", "Patch 04: HLS Downloads"])

    # Export
    print("==> Exporting modular patches to patches/...")
    p1_diff = run(["git", "diff", "HEAD~4..HEAD~3"]).stdout
    with open(os.path.join(patches_dir, "01-branding-side-by-side.patch"), "w", encoding="utf-8", newline="\n") as f:
        f.write(p1_diff)
    print("Exported 01-branding-side-by-side.patch")

    p2_diff = run(["git", "diff", "HEAD~3..HEAD~2"]).stdout
    with open(os.path.join(patches_dir, "02-app-updater.patch"), "w", encoding="utf-8", newline="\n") as f:
        f.write(p2_diff)
    print("Exported 02-app-updater.patch")

    p3_diff = run(["git", "diff", "HEAD~2..HEAD~1"]).stdout
    with open(os.path.join(patches_dir, "03-live-tv.patch"), "w", encoding="utf-8", newline="\n") as f:
        f.write(p3_diff)
    print("Exported 03-live-tv.patch")

    p4_diff = run(["git", "diff", "HEAD~1..HEAD"]).stdout
    with open(os.path.join(patches_dir, "04-hls-downloads.patch"), "w", encoding="utf-8", newline="\n") as f:
        f.write(p4_diff)
    print("Exported 04-hls-downloads.patch")

finally:
    shutil.rmtree(temp_dir, ignore_errors=True)

print("==> Done! You can now test with scripts/test-patch-apply.ps1")
