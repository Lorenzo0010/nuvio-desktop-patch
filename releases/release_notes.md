## Novita in Nuvio Plus Desktop 0.1.22.8-alpha

### Risoluzione Errore HTTP 410 e Probing HLS
- **Probing HLS su flussi mascherati**: Aggiunto il controllo preliminare tramite DownloadsRepository.probeIsHls su tutti gli stream prima del download. Se uno stream si presenta con estensione fittizia (es. .mp4) ma e un indice playlist HLS, l'applicazione apre correttamente il selettore HLS invece di fallire con errore HTTP 410 su download diretto.
- **Risoluzione Debrid preliminare**: Se uno stream e gestito da Debrid, viene prima risolto l'URL effettivo prima di avviare il probing HLS o l'accodamento del download.

### Risoluzione SSL Handshake / Certificati
- Configurato 	rustAllManager e hostname verifier permissivo nel client OkHttp del download manager desktop (DownloadsPlatformDownloader.desktop.kt), prevenendo errori di connessione SSL Handshake su nodi CDN e sslip.io.

### Windows MSI Upgrade
- **ProductVersion**: 1.1.2208 (consente l'aggiornamento automatico e diretto sopra le release precedenti senza disinstallazione).
