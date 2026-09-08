## Novità in Nuvio Plus Desktop 0.1.22.9-alpha

### 🚀 Allineamento Completo con l'Ecosistema Mobile (Nuvio Plus)
- **Porting Funzionalità Plus**: Portate su Desktop tutte le funzionalità avanzate della versione mobile:
  - Download HLS multitraccia con supporto audio e sottotitoli integrati.
  - Opzioni Patches Plus nelle impostazioni: prefetching dei flussi, selezione sorgente preferita (Tutti, Solo Addon con fallback, Solo Plugin Repository), filtro per Addon o Repository specifici.
  - Download diretto dei film tramite pulsante dedicato nella sezione Hero Desktop e nelle schede/liste episodi delle serie.

### ⏱️ Timer Addon Esteso a 30 Secondi
- **Risoluzione Flussi**: Tempo di attesa per la risoluzione dei flussi da Addon raddoppiato a **30 secondi**, garantendo il reperimento ottimale dei flussi Debrid/HTTP più lenti prima di tentare fallback alternativi.

### 🔄 Animazione di Avanzamento Live sui Pulsanti di Download
- **Indicatore Determinato Circolare**: I pulsanti di download sia per film che per episodi mostrano in tempo reale una CircularProgressIndicator animata sincronizzata con la percentuale esatta di completamento dello scaricamento (0%..100%).
- **Feedback Continuo**: Rotazione indeterminata durante la fase di analisi/aggancio stream e anello circolare con percentuale numerica a download avviato.

### 🛡️ Continuità e Sicurezza in Background
- **Zero Interruzioni**: La navigazione fuori dalla pagina dei dettagli del titolo, l'esplorazione di altri contenuti o la riduzione dell'app a icona non interrompono né la ricerca né il download in corso, che prosegue in modo trasparente e in background.

### 🖱️ Azione Rapida Tasto Destro
- Facendo clic con il tasto destro del mouse sul pulsante di download viene visualizzato direttamente lo sheet di selezione manuale delle tracce e dei flussi.

### 📦 Installatore Windows MSI
- **ProductVersion**: 1.1.2209 (aggiornamento pulito e diretto sopra le versioni precedenti senza disinstallazione preventiva).
