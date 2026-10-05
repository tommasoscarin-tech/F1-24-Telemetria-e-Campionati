# PROMPT 11 — App Flutter: tablet, permessi, esportazione, README

Leggi `PROGETTO.md` e il codice di `app/`.

Compito:
1. **Tablet:** layout adattivo; in orizzontale due colonne (KPI + grafico a sinistra, Live + tabella a destra), su telefono una colonna. Controlli con area di tocco di almeno 44 px.
2. **iOS:** `NSLocalNetworkUsageDescription` in `Info.plist` con testo in italiano; spiega nell'app che in background iOS sospende il socket UDP e che serve tenere l'app aperta con lo schermo acceso.
3. **Android:** permessi `INTERNET`, `ACCESS_WIFI_STATE` e, se serve, il lock multicast; indica se conviene un servizio in primo piano per non perdere pacchetti a schermo spento, senza implementarlo se non necessario.
4. **Impostazioni extra:** porta UDP, salva giri tagliati sì/no, scarta out-lap/in-lap sì/no, esporta e importa il database come file, elimina dati per giocatore o pista.
5. **`app/README.md`** in italiano: build passo passo per Android (APK/AAB) e iOS (Mac con Xcode, firma), impostazioni da fare in F1 24, risoluzione dei problemi.
6. **Verifica finale di parità:** controlla una per una le funzioni di `PROGETTO.md` (multi-giocatore, filtri, KPI, grafico, feedback, tabella, esclusione giri, Live, tema) e riportami una tabella "fatto / non verificato / differenze".

Vincoli: dichiara con onestà cosa hai provato davvero (emulatore, dispositivo, gioco reale) e cosa no. Fine del lavoro: fermati.
