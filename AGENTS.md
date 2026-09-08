# Protocollo di Aggiornamento Nuvio Desktop (AGENTS.md)

Questo documento definisce il protocollo standard e obbligatorio che l'agente AI (Antigravity) deve seguire ogni volta che l'utente richiede di **"aggiornare la versione di Nuvio Desktop"** o di verificare/applicare le patch all'ultima versione upstream di Nuvio Desktop.

## ⚡ Token-Saver Mode (alta efficienza token, obbligatorio)
1. **Lettura mirata:** mai scansionare intero workspace o caricare directory intere; leggere solo file/range strettamente necessari. Ignorare cache, build, log, dipendenze (es. `node_modules`, `venv`, `dist`, `target`) e binari.
2. **Editing compatto:** applicare solo diff/patch mirate o funzione/classe aggiornata; non ristampare mai file interi o righe invariate per contesto.
3. **Risposte concise:** minimo preambolo/spiegazione, solo cosa cambiato e perché in max 2-3 frasi; niente boilerplate discorsivo.
4. **Isolamento task:** ogni richiesta è operazione puntuale; se contesto precedente non serve, suggerire riavvio chat per liberare memoria.

---

## 🎯 Obiettivo del Flusso
Mantenere il fork e le patch personalizzate perfettamente allineate con l'upstream ufficiale (`https://github.com/NuvioMedia/NuvioDesktop.git`, branch `Dev`), isolando i conflitti, aggiornando le patch modulari in `patches/` e generando una nuova Release desktop firmata/pacchettizzata e funzionante.

---

## 🔗 Repository Collegati (Ecosistema Nuvio Plus)
Questo repository (`Nuvio Desktop` / `nuvio-desktop-patch`) e il repository Mobile (`F:\GitHub\nuvio`, `Nuvio Mobile` / `nuvio-patch`) sono **strettamente collegati** e formano l'ecosistema multipiattaforma **Nuvio Plus**:
- **Desktop**: `F:\GitHub\nuviodesktop` (Remote fork: `Lorenzo0010/nuvio-desktop-patch`, Upstream: `https://github.com/NuvioMedia/NuvioDesktop.git`, branch `Dev`)
- **Mobile / Android**: `F:\GitHub\nuvio` (Remote fork: `Lorenzo0010/nuvio-patch`, Upstream: `https://github.com/NuvioMedia/NuvioMobile.git`, branch `cmp-rewrite`)

### Principi di Condivisione e Allineamento:
1. **Feature Parity e Logica Condivisa**: Le feature Plus introdotte (es. Live TV con M3U parser/storage, download e gestione multitraccia HLS, patch ai plugin JS/bridges, prefetching dei link di streaming, configurazioni branding/aggiornamenti) seguono la stessa architettura logica. Quando si implementa, ottimizza o corregge una feature su un repository, verificare se la medesima logica o fix è applicabile o deve essere sincronizzata nell'altro.
2. **Architettura Compose Multiplatform**: Entrambe le codebase sono basate su Kotlin Multiplatform / Compose Multiplatform (`composeApp`), pertanto molti file di UI, viewmodel, modelli dati o utilità possono essere condivisi o adattati direttamente tra Desktop e Mobile.
3. **Sincronizzazione Mobile → Desktop**: Le modifiche ai file `commonMain/` e `desktopMain/` del repo mobile (patch 04, 05, 07) devono essere portate nel desktop escludendo `androidMain/`, `iosMain/` e widget. Vedi `SYNC_FROM_MOBILE.md` per la procedura dettagliata.

---

## 🛡️ Regola Assoluta di Isolamento (Side-by-Side)
1. **Cartelle Dati Indipendenti**: L'applicazione Nuvio Plus Desktop DEVE utilizzare percorsi di persistenza separati rispetto all'app originale Nuvio:
   - Windows AppData: `%APPDATA%\NuvioPlus` (invece di `%APPDATA%\Nuvio`)
   - Windows Cache: `%LOCALAPPDATA%\NuvioPlus\Cache` (invece di `%LOCALAPPDATA%\Nuvio\Cache`)
   - macOS Application Support: `Library/Application Support/NuvioPlus`
   - Linux Config: `~/.config/nuvioplus`
2. **Identificatori di Pacchetto**:
   - `packageName`: `NuvioPlus`
   - `menuGroup`: `Nuvio Plus`
   - `windowsMsiUpgradeUuid`: `d7e954a2-73a1-4cf4-912b-2856417726d1`
   - Window Title: `Nuvio Plus`
   Questo impedisce qualsiasi sovrascrittura o conflitto con l'installazione ufficiale presente sul computer dell'utente.

---

## 🏷️ Regola di Versionamento
1. **Versione Base Upstream**: La versione base (es. `0.1.22-alpha`) rispecchia la versione upstream in `build.gradle.kts`. Va cambiata SOLO in presenza di aggiornamenti upstream.
2. **Incremento Patch Utente (`0.1.22.x`)**: Tutte le modifiche, bugfix o personalizzazioni Plus devono incrementare il suffisso `.x` (es. `0.1.22.1`, `0.1.22.2`).
3. **File Sorgente della Versione**: l'unica fonte è `NuvioDesktop/composeApp/Configuration/DesktopVersion.properties` (`VERSION_NAME` = `<versione>`, `VERSION_CODE` = intero incrementale). Il valore effettivo è quello della patch 07 applicata per ultima. Per un version bump: modifica il file nella copia `NuvioDesktop/`, poi rigenera la patch 07 (vedi § Sviluppo).
4. **Aggiornamento in-app e Tag Release**: Il tag di release segue il formato `<versione>` per consentire all'updater in-app (`AppUpdaterPlatform.desktop.kt`) di rilevare e installare gli aggiornamenti da `Lorenzo0010/nuvio-desktop-patch`.

---

## 🔧 Ciclo di Sviluppo (come si agisce sul repo)

Le modifiche al codice **non** avvengono nel repo root (che non contiene sorgenti), ma nella copia di lavoro `NuvioDesktop/`:

1. **Modifica** i file in `NuvioDesktop/` (già allineata a `.last_built_upstream_sha` con tutte le patch applicate).
2. **Rigenera le patch** interessate. Dopo aver aggiunto i file a staging con `git add`, usa `git diff --cached` puntando ai file specifici di ogni patch:
   - **Patch 04** (downloads, HLS, core, player, streams, strings):
     ```powershell
     cd NuvioDesktop
     git add composeApp/src/commonMain composeApp/src/desktopMain
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
     ```
   - **Patch 06** (stream-prefetch, settings Plus, details):
     ```powershell
     git diff --cached `
       -- "composeApp/src/commonMain/kotlin/com/nuvio/app/features/details" `
          "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/PatchesPlusSettingsPage.kt" `
          "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/SettingsModels.kt" `
          "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/SettingsRootPage.kt" `
          "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/SettingsScreen.kt" `
          "composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/SettingsSearch.kt" `
       > ..\patches\06-stream-prefetch.patch
     ```
   - **Patch 07** (versione):
     ```powershell
     git add composeApp/Configuration/DesktopVersion.properties
     git diff --cached -- composeApp/Configuration/DesktopVersion.properties > ..\patches\07-version-bump.patch
     ```
   - Se aggiungi **nuovi file** `commonMain` o `desktopMain`, aggiungili al path della patch corrispondente.
3. **Testa** l'applicabilità di tutte le patch su upstream fresco:
   - PowerShell: `powershell -ExecutionPolicy Bypass -File .\scripts\test-patch-apply.ps1`
   - Bash: `bash ./scripts/test-patch-apply.sh`
4. **Gestione conflitti** (se una patch fallisce): identifica il file dall'output git, analizza il nuovo codice upstream, reintegra manualmente le feature Plus preservando entrambi, rigenera la patch.
5. Per riallineare da zero la copia di lavoro: clone upstream fresco + applica le patch in ordine numerico con `git apply --3way`.

---

## 🔄 Sincronizzazione Upstream

1. Identifica l'ultimo commit di `upstream/Dev`:
   ```powershell
   git ls-remote https://github.com/NuvioMedia/NuvioDesktop.git refs/heads/Dev
   ```
2. Confronta lo SHA con `.last_built_upstream_sha`. Se coincidono e non c'è richiesta di force-update, il repo è già aggiornato.
3. Altrimenti: clone pulito in `NuvioDesktop/` con `git clone --depth 1 --branch Dev`, applica le patch in ordine con `git apply --3way`, risolvi i conflitti (§ Sviluppo punto 4), rigenera le patch, aggiorna `.last_built_upstream_sha` **solo dopo** build+test verificati.

---

## 📋 Fasi Operative per l'Agente (Aggiornamento Upstream)

### Fase 1: Verifica dello Stato Upstream
1. Identifica l'ultimo commit di `upstream/Dev`:
   ```bash
   git ls-remote https://github.com/NuvioMedia/NuvioDesktop.git refs/heads/Dev
   ```
2. Confronta lo SHA con `.last_built_upstream_sha`.
3. Se gli SHA coincidono e non è richiesto un force-update, informa l'utente che il repository desktop è già aggiornato.

### Fase 2: Clone Pulito in Directory di Lavoro
1. Clona l'upstream ufficiale in `NuvioDesktop`:
   ```bash
   git clone --depth 1 --branch Dev https://github.com/NuvioMedia/NuvioDesktop.git NuvioDesktop
   ```
2. Assicurati che esista un file vuoto `local.properties` nella root di `NuvioDesktop`.

### Fase 3: Applicazione Sequenziale delle Patch Modulari
Le patch si trovano in `patches/` e vanno applicate in ordine numerico:
1. `patches/01-branding-side-by-side.patch` (Branding Nuvio Plus, isolamento AppData/Cache, configurazione Gradle)
2. `patches/02-app-updater.patch` (Reindirizzamento updater su `Lorenzo0010/nuvio-desktop-patch`)
3. `patches/03-live-tv.patch` (Funzionalità Live TV, storage canali M3U, drawer in-player, sidebar e navigation bar desktop)
4. `patches/04-hls-downloads.patch` (Download offline e streaming HLS multitraccia, decrittazione hardware AES-128, picker cartella e gestione download)
5. `patches/05-desktop-plugins-fix.patch` (Runtime plugin QuickJS per desktop e correzioni host bindings)
6. `patches/06-stream-prefetch.patch` (Menu impostazioni Patches Plus e precaricamento sorgenti streaming in background su MetaDetailsScreen)
7. `patches/07-version-bump.patch` (Incremento versione desktop alla versione corrente)

Esegui lo script di test:
- PowerShell: `powershell -ExecutionPolicy Bypass -File .\scripts\test-patch-apply.ps1`
- Bash: `bash ./scripts/test-patch-apply.sh`

### Fase 4: Runtime Nativo MPV e WebView2
1. Copia i binari nativi da `assets/native/windows/`:
   - `player_bridge.dll` in `composeApp/build/native/windows/player_bridge.dll` (permette di evitare MSVC/cl.exe)
   - `WebView2Loader.dll` in `composeApp/src/desktopMain/native/windows/runtime/`
2. Verifica che `libmpv-2.dll` sia presente nel runtime.

---

## 🏗️ Compilazione Desktop in Locale

Esegui la build **nella directory con le patch applicate** (`NuvioDesktop/`), mai nel repo root.

### Prerequisiti
1. JDK 17+ installato e `JAVA_HOME` impostato.
2. `local.properties` presente nella root di `NuvioDesktop/` (mai committato).
3. Asset copiati: `assets/native/windows/*.dll` → `composeApp/build/native/windows/` e `composeApp/src/desktopMain/native/windows/runtime/`.
4. `VERSION_NAME`/`VERSION_CODE` già al valore target (via patch 07).

### Comandi (PowerShell)

```powershell
cd F:\GitHub\nuviodesktop\NuvioDesktop

# JAR eseguibile (sviluppo/test rapido)
.\gradlew.bat :composeApp:desktopJar --no-daemon

# Esecuzione locale diretta
.\gradlew.bat :composeApp:run --no-daemon

# Installer MSI (Windows, per la release)
.\gradlew.bat :composeApp:packageMsi --no-daemon
```

### Output e verifica
- MSI in `composeApp\build\compose\binaries\main\msi\NuvioPlus-<versione>.msi`
- JAR in `composeApp\build\compose\jars\`
- Verifica `applicationId=NuvioPlus`, `versionName=<versione>` prima di pubblicare.

### Rinomina (release)
```powershell
Copy-Item composeApp\build\compose\binaries\main\msi\NuvioPlus-<versione>.msi `
          ..\releases\NuvioPlus_<versione>_windows.msi
```

---

## 🚀 Pubblicazione su GitHub (commit, push, release)

1. **Aggiorna** `releases/release_notes.md` con la sezione `## Novità in Nuvio Plus Desktop <versione>` (è l'unico file tracciato sotto `releases/`, i MSI restano locali fino all'upload).
2. **Commit e push** su `origin/main` (solo file tracciati: patch rigenerate, script, `releases/release_notes.md`, `.last_built_upstream_sha` se in sync). Convenzioni osservate:
   - `feat(desktop): <descrizione> (v<versione>)`
   - `fix(<area>): <descrizione> (v<versione>)`
   - `chore: aggiorna patch <NN> ... v<versione>`
   - `docs: aggiorna note di rilascio per v<versione>`

   ```powershell
   cd F:\GitHub\nuviodesktop
   git add patches/ releases/release_notes.md
   git commit -m "feat(desktop): <descrizione> (v<versione>)"
   git push origin main
   ```

3. **Crea la GitHub Release** sul fork `Lorenzo0010/nuvio-desktop-patch` (tag = versione pulita, creato dal comando se assente). Esegui il comando nella root `F:\GitHub\nuviodesktop`:
   ```powershell
   gh release create "<versione>" `
     releases\NuvioPlus_<versione>_windows.msi `
     --title "Nuvio Plus Desktop <versione>" `
     --notes-file releases\release_notes.md `
     --repo Lorenzo0010/nuvio-desktop-patch
   ```

4. **Verifica** con `gh release view <versione> --repo Lorenzo0010/nuvio-desktop-patch`: asset MSI presente, tag corretto, note pubblicate.

---

## ✅ Checklist Rapida per l'Agente

- [ ] Verificato ultimo commit upstream via `git ls-remote` e confrontato con `.last_built_upstream_sha`
- [ ] Sviluppato in `NuvioDesktop/`; nuovi file aggiunti al path corretto nel comando `git diff --cached` della patch corrispondente
- [ ] Patch 04, 06, 07 rigenerate con `git diff --cached` e testate (`test-patch-apply.ps1`)
- [ ] Regola di versionamento rispettata: `X.Y.Z` da upstream, `.W` dall'utente; versione effettiva via patch 07
- [ ] Nessun suffisso/hash extra in `VERSION_NAME`, solo `X.Y.Z.W-alpha`
- [ ] `local.properties` presente nella dir di build (mai committato)
- [ ] Build con `.\gradlew.bat :composeApp:packageMsi --no-daemon`; verificato `applicationId`/`versionName`
- [ ] MSI rinominato in `releases/`; `releases/release_notes.md` aggiornata
- [ ] Commit + push su `origin/main` con messaggi convenzionali
- [ ] Release creata con `gh release create <versione>` e verificata con `gh release view <versione>`
