# Istruzioni per Sincronizzare le Modifiche Mobile → Desktop (Nuvio Plus)

> Questo documento è destinato a un agente AI (es. Antigravity, Claude, Gemini) che deve portare le modifiche introdotte nel repository **Nuvio Mobile** nel repository **Nuvio Desktop**, escludendo le feature esclusivamente Android/iOS (es. widget, notifiche Android, foreground service).

---

## 📁 Posizioni su Disco

| Repository | Percorso locale | Remote fork | Upstream |
|---|---|---|---|
| **Nuvio Mobile** | `F:\GitHub\nuvio` | `Lorenzo0010/nuvio-patch` | `https://github.com/NuvioMedia/NuvioMobile.git` branch `cmp-rewrite` |
| **Nuvio Desktop** | `F:\GitHub\nuviodesktop` | `Lorenzo0010/nuvio-desktop-patch` | `https://github.com/NuvioMedia/NuvioDesktop.git` branch `Dev` |

### Struttura rilevante

```
F:\GitHub\nuvio\                        ← repo mobile (root)
├── patches/
│   ├── 01-branding-and-config.patch
│   ├── 02-app-updater.patch
│   ├── 03-live-tv.patch
│   ├── 04-plugin-hls-downloads.patch   ← principale: downloads, HLS, coda
│   ├── 05-bugfixes.patch               ← fix UI/core
│   ├── 06-launcher-widget.patch        ← ⛔ ESCLUDI (solo Android widget)
│   └── 07-stream-prefetch.patch        ← prefetch, settings, details
├── scripts/
│   ├── update-patch-04.ps1
│   ├── update-patch-07.ps1
│   └── test-patch-apply.ps1
└── NuvioMobile/                        ← copia di lavoro upstream + patch applicate

F:\GitHub\nuviodesktop\                 ← repo desktop (root)
├── patches/
│   ├── 01-branding-side-by-side.patch
│   ├── 02-app-updater.patch
│   ├── 03-live-tv.patch
│   ├── 04-hls-downloads.patch          ← equivalente mobile 04
│   ├── 05-desktop-plugins-fix.patch
│   ├── 06-stream-prefetch.patch        ← equivalente mobile 07 + parte 05
│   └── 07-version-bump.patch           ← solo versione
└── NuvioDesktop/                       ← clone upstream con patch applicate
```

---

## 🔄 Corrispondenza Patch Mobile → Desktop

| Patch Mobile | Contenuto | Patch Desktop equivalente |
|---|---|---|
| `04-plugin-hls-downloads.patch` | Downloads HLS, coda, progress, auto-download, filtri addon/repo | `04-hls-downloads.patch` |
| `05-bugfixes.patch` | Fix UI: `DisintegrationEffect.kt`, `PosterZoomActionOverlay.kt` | incluso in `04-hls-downloads.patch` o `06-stream-prefetch.patch` |
| `07-stream-prefetch.patch` | Settings, prefetch, MetaDetails, PatchesPlusSetting | `06-stream-prefetch.patch` |
| `06-launcher-widget.patch` | Widget Android home screen | **⛔ NON PORTARE** |

---

## 🎯 Obiettivo del Task

Portare nel repository Desktop (`F:\GitHub\nuviodesktop`) tutte le modifiche introdotte nel repository Mobile (`F:\GitHub\nuvio`) a partire dall'ultimo commit di sincronizzazione, **escludendo**:

- Tutto ciò che è in `androidMain/` o `iosMain/`
- I widget (`06-launcher-widget.patch`, qualsiasi file con "widget" nel path)
- Il foreground service Android (`DownloadsForegroundService.kt`, `DownloadsNotificationActionReceiver.kt`)
- File `.xcconfig` e cartella `iosApp/`
- Manifest Android (`AndroidManifest.xml`), risorse drawable/layout Android

**Includere**:
- Tutti i file in `commonMain/` (Kotlin, resources/strings)
- Tutti i file in `desktopMain/`
- I file `build.gradle.kts` se contengono dipendenze nuove rilevanti per desktop

---

## 📋 Procedura Operativa

### Passo 1 — Identifica le modifiche mobile recenti

```powershell
# Vedi i commit mobile recenti
git -C F:\GitHub\nuvio log --oneline -20

# Lista file cambiati (sostituisci SHA_PREC con l'ultimo commit già portato)
git -C F:\GitHub\nuvio diff <SHA_PREC> HEAD --name-only
```

### Passo 2 — Estrai i file `commonMain` e `desktopMain` dalle patch mobile

Salva il seguente script Python in un file temporaneo ed eseguilo:

```python
import re, pathlib

DESKTOP_CLONE = r"F:/GitHub/nuviodesktop/NuvioDesktop"

def extract_and_apply(patch_path, exclude_patterns=None):
    if exclude_patterns is None:
        exclude_patterns = ['androidMain', 'iosMain', 'widget', 'xcconfig', 'iosApp']
    
    with open(patch_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    parts = re.split(r'(?=^diff --git )', content, flags=re.MULTILINE)
    
    for part in parts:
        m = re.match(r'diff --git a/(.+?) b/(.+)', part)
        if not m:
            continue
        filepath = m.group(2)
        
        if any(p in filepath for p in exclude_patterns):
            continue
        if 'commonMain' not in filepath and 'desktopMain' not in filepath:
            continue
        
        lines = part.splitlines(keepends=True)
        result_lines = []
        in_hunk = False
        for line in lines:
            if line.startswith('@@'):
                in_hunk = True
                continue
            if not in_hunk:
                continue
            if line.startswith('diff --git') or line.startswith('index ') \
               or line.startswith('---') or line.startswith('+++'):
                in_hunk = False
                continue
            if line.startswith('+'):
                result_lines.append(line[1:])
            elif line.startswith(' '):
                result_lines.append(line[1:])
        
        if not result_lines:
            continue
        
        dest = pathlib.Path(DESKTOP_CLONE) / filepath
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(''.join(result_lines), encoding='utf-8')
        print(f"OK: {filepath}")

# Applica patch nell'ordine corretto
extract_and_apply(r"F:/GitHub/nuvio/patches/04-plugin-hls-downloads.patch")
extract_and_apply(r"F:/GitHub/nuvio/patches/05-bugfixes.patch")
extract_and_apply(r"F:/GitHub/nuvio/patches/07-stream-prefetch.patch")
```

> **Nota**: lo script sovrascrive ogni file con il contenuto finale della patch. Dopo aver eseguito, controlla manualmente i file desktop-specifici elencati nella sezione seguente.

### Passo 3 — Verifica i file scritti nel clone e metti in staging

```powershell
cd F:\GitHub\nuviodesktop\NuvioDesktop

git status --short
git add composeApp/src/commonMain composeApp/src/desktopMain
```

### Passo 4 — Rigenera le patch desktop 04 e 06

```powershell
cd F:\GitHub\nuviodesktop\NuvioDesktop

# Patch 04 (downloads, core, player, streams, strings)
git diff --cached `
  -- "composeApp/src/commonMain/composeResources" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/AppShellComponents.kt" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/MainAppContent.kt" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/MainTabsDestination.kt" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/core" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/features/downloads" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/features/player" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/DownloadsSettingsPage.kt" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/DownloadsSettingsScreen.kt" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/NetworkSettingsRepository.kt" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams" `
     "composeApp/src/desktopMain" `
  > ..\patches\04-hls-downloads.patch

# Patch 06 (stream-prefetch, settings Plus, details)
git diff --cached `
  -- "composeApp/src/commonMain/kotlin/com/nuvio/app/features/details" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/PatchesPlusSettingsPage.kt" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/SettingsModels.kt" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/SettingsRootPage.kt" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/SettingsScreen.kt" `
     "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/SettingsSearch.kt" `
  > ..\patches\06-stream-prefetch.patch
```

### Passo 5 — Aggiorna la versione (patch 07)

La versione desktop segue lo schema `0.1.22.X-alpha`. Incrementa X:

```powershell
# Leggi la versione corrente
Get-Content F:\GitHub\nuviodesktop\NuvioDesktop\composeApp\Configuration\DesktopVersion.properties

# Modifica il file con la nuova versione
# Esempio: VERSION_NAME=0.1.22.11-alpha, VERSION_CODE=28

# Rigenera la patch 07
cd F:\GitHub\nuviodesktop\NuvioDesktop
git add composeApp/Configuration/DesktopVersion.properties
git diff --cached -- composeApp/Configuration/DesktopVersion.properties > ..\patches\07-version-bump.patch
```

### Passo 6 — Commit e push nel repo desktop

```powershell
cd F:\GitHub\nuviodesktop

git add patches/
git commit -m "feat(desktop): port mobile changes vX.Y.Z.A-B (descrizione breve) and bump to vX.Y.Z.N-alpha"
git push origin main
```

### Passo 7 — Crea la Release GitHub

```powershell
cd F:\GitHub\nuviodesktop

gh release create "<versione>" `
  --title "Nuvio Plus Desktop <versione>" `
  --notes "Port delle modifiche mobile: <descrizione>" `
  --repo Lorenzo0010/nuvio-desktop-patch
```

---

## ⚠️ Regole di Esclusione (NON portare)

| File / Pattern | Motivo |
|---|---|
| `androidMain/` | Solo Android |
| `iosMain/` | Solo iOS |
| `iosApp/` | Progetto Xcode |
| `*widget*` (qualsiasi path) | Widget Android home screen |
| `DownloadsForegroundService.kt` | Servizio Android |
| `DownloadsNotificationActionReceiver.kt` | Broadcast receiver Android |
| `Mp4ParserRemux.kt` (se in androidMain) | Remuxing Android-only |
| `AndroidManifest.xml` | Manifest Android |
| `drawable*/`, `layout*/`, `xml/` | Risorse Android |
| `Version.xcconfig`, `*.plist` | Configurazione iOS |

---

## 🔑 File Desktop-Specifici (confronta prima di sovrascrivere)

I seguenti file nel clone `NuvioDesktop/` hanno implementazioni desktop-specifiche che non devono essere sostituite ciecamente:

| File | Nota |
|---|---|
| `DownloadsPlatformDownloader.desktop.kt` | Usa threading JVM, FileChannel. Confronta le API con la versione mobile. |
| `DownloadsStorage.desktop.kt` | Percorso `%APPDATA%\NuvioPlus`. Non alterare il path. |
| `DownloadsClock.desktop.kt` | Implementazione JVM (`System.currentTimeMillis`). |
| `AppUpdaterPlatform.desktop.kt` | Punta a `Lorenzo0010/nuvio-desktop-patch`. Non sovrascrivere. |
| `SharePlatform.desktop.kt` | Apertura file/URL con Desktop API Java. |
| `InAppLogger.desktop.kt` | Logger su file in `%APPDATA%\NuvioPlus\logs`. |

---

## 🏷️ Versionamento

- Schema: `MAJOR.MINOR.PATCH.BUILD-alpha` (es. `0.1.22.10-alpha`)
- `MAJOR.MINOR.PATCH` rispecchia la versione upstream NuvioDesktop
- `BUILD` è incrementato ad ogni port/modifica personalizzata
- `VERSION_CODE` è incrementato di 1 ad ogni bump
- Il file da modificare è `NuvioDesktop/composeApp/Configuration/DesktopVersion.properties`
- Non modificare mai `build.gradle.kts` per la versione: si usa solo il `.properties`

---

## ✅ Checklist Rapida

- [ ] Identificati i commit mobile non ancora portati (confronto SHA)
- [ ] Script Python eseguito per estrarre file `commonMain`/`desktopMain` dalle patch 04, 05, 07 mobile
- [ ] File desktop-specifici verificati manualmente (nessuna regressione)
- [ ] `git status` nel clone mostra solo le modifiche attese
- [ ] Patch 04 e 06 desktop rigenerate con `git diff --cached`
- [ ] Versione desktop incrementata (patch 07 rigenerata)
- [ ] Commit su `F:\GitHub\nuviodesktop` con messaggio convenzionale
- [ ] Push su `origin/main` (`Lorenzo0010/nuvio-desktop-patch`)
- [ ] Release GitHub creata con `gh release create`
