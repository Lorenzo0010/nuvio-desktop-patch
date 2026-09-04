# Nuvio Plus Desktop (Patch Repository)

Repository dedicato per il porting desktop delle patch **Nuvio Plus** sull'applicazione ufficiale [NuvioDesktop](https://github.com/NuvioMedia/NuvioDesktop) (branch `Dev`).

## ✨ Funzionalità Plus
- 📺 **Live TV Integrata**: Riproduzione flussi IPTV/M3U, gestione playlist, preferiti, canali recenti, e drawer rapido per il cambio canale durante la riproduzione con MPV nativo.
- 🛡️ **Isolamento Side-by-Side (Zero Conflitti)**: Funziona in totale coesistenza con l'app Nuvio ufficiale già installata sul computer, utilizzando una cartella di configurazione e cache separata (`%APPDATA%\NuvioPlus` e `%LOCALAPPDATA%\NuvioPlus\Cache`).
- 🔄 **Aggiornamenti In-App Dedicati**: Reindirizzamento dell'updater in-app sulle release di questo repository (`Lorenzo0010/nuvio-desktop-patch`).

## 📁 Struttura del Progetto
- `patches/`: Patch modulari applicabili all'upstream NuvioDesktop
  - `01-branding-side-by-side.patch`: Isolamento archiviazione e configurazione del pacchetto desktop
  - `02-app-updater.patch`: Connessione a `Lorenzo0010/nuvio-desktop-patch`
  - `03-live-tv.patch`: Implementazione completa della Live TV e integrazione con la UI desktop
- `scripts/`: Script di test per verificare e applicare le patch in modo automatico (`test-patch-apply.ps1`, `test-patch-apply.sh`)
- `assets/native/windows/`: Librerie native e player bridge precompilati per Windows x64
- `AGENTS.md`: Protocollo operativo standard per l'aggiornamento automatico
