# Protocollo di Aggiornamento Nuvio Desktop (AGENTS.md)

Questo documento definisce il protocollo standard e obbligatorio che l'agente AI (Antigravity) deve seguire ogni volta che l'utente richiede di **"aggiornare la versione di Nuvio Desktop"** o di verificare/applicare le patch all'ultima versione upstream di Nuvio Desktop.

---

## 🎯 Obiettivo del Flusso
Mantenere il fork e le patch personalizzate perfettamente allineate con l'upstream ufficiale (`https://github.com/NuvioMedia/NuvioDesktop.git`, branch `Dev`), isolando i conflitti, aggiornando le patch modulari in `patches/` e generando una nuova Release desktop firmata/pacchettizzata e funzionante.

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
3. **Aggiornamento in-app e Tag Release**: Il tag di release segue il formato `<versione>-<short_sha>` per consentire all'updater in-app (`AppUpdaterPlatform.desktop.kt`) di rilevare e installare gli aggiornamenti da `Lorenzo0010/nuvio-desktop-patch`.

---

## 📋 Fasi Operative per l'Agente

### Fase 1: Verifica dello Stato Upstream
1. Identifica l'ultimo commit di `upstream/Dev`:
   ```bash
   git ls-remote https://github.com/NuvioMedia/NuvioDesktop.git refs/heads/Dev
   ```
2. Confronta lo SHA con `.last_built_upstream_sha`.
3. Se gli SHA coincidono e non è richiesto un force-update, informa l'utente che il repository desktop è già aggiornato.

---

### Fase 2: Clone Pulito in Directory di Lavoro
1. Clona l'upstream ufficiale in `NuvioDesktop` (o directory temporanea):
   ```bash
   git clone --depth 1 --branch Dev https://github.com/NuvioMedia/NuvioDesktop.git NuvioDesktop
   ```
2. Assicurati che esista un file vuoto `local.properties` nella root di `NuvioDesktop`.

---

### Fase 3: Applicazione Sequenziale delle Patch Modulari
Le patch si trovano in `patches/` e vanno applicate in ordine numerico:
1. `patches/01-branding-side-by-side.patch` (Branding Nuvio Plus, isolamento AppData/Cache, configurazione Gradle)
2. `patches/02-app-updater.patch` (Reindirizzamento updater su `Lorenzo0010/nuvio-desktop-patch`)
3. `patches/03-live-tv.patch` (Funzionalità Live TV, storage canali M3U, drawer in-player, sidebar e navigation bar desktop)

Esegui lo script di test:
- PowerShell: `powershell -ExecutionPolicy Bypass -File .\scripts\test-patch-apply.ps1`
- Bash: `bash ./scripts/test-patch-apply.sh`

---

### Fase 4: Runtime Nativo MPV e WebView2
1. Copia i binari nativi da `assets/native/windows/`:
   - `player_bridge.dll` in `composeApp/build/native/windows/player_bridge.dll` (permette di evitare MSVC/cl.exe)
   - `WebView2Loader.dll` in `composeApp/src/desktopMain/native/windows/runtime/`
2. Verifica che `libmpv-2.dll` sia presente nel runtime.

---

### Fase 5: Compilazione, Test e Pubblicazione
1. **Compilazione Desktop**:
   ```bash
   .\gradlew.bat :composeApp:desktopJar --no-daemon
   ```
2. **Esecuzione Test Locale**:
   ```bash
   .\gradlew.bat :composeApp:run --no-daemon
   ```
3. **Commit, Push e Release**:
   - Aggiorna `.last_built_upstream_sha`
   - Esegui commit e push sul repository `Lorenzo0010/nuvio-desktop-patch`
   - Pubblica la release GitHub: `gh release create <tag> <file_artefatto> --title "Nuvio Plus Desktop <versione>"`
