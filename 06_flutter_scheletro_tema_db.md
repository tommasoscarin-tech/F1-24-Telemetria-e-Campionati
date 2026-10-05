# PROMPT 06 — App Flutter: scheletro, tema, database

Leggi `PROGETTO.md` e `schema.sql`. L'app va nella cartella `app/` (Android, iOS, tablet); il progetto Python non si tocca.

Compito:
1. Crea il progetto: `flutter create app --org com.f1telemetry --platforms android,ios`. Dichiara in una riga perché Flutter e non React Native.
2. Dipendenze ragionevoli: `drift` (o `sqflite`), `fl_chart`, `provider` o `riverpod`, `shared_preferences`, `wakelock_plus`, `network_info_plus`, `path_provider`. Font Teko e Titillium Web **inclusi negli asset**, non scaricati da internet.
3. Tema scuro con i colori e i font della sezione Design di `PROGETTO.md`.
4. Navigazione: barra in basso su telefono, `NavigationRail` su tablet, con 4 sezioni vuote: Dashboard, Live, Giri, Impostazioni.
5. Database locale con le stesse tabelle e colonne di `schema.sql` (users, circuits, sessions, laps con `excluded`), più i modelli Dart e un repository con le operazioni base (crea giocatore da IP, rinomina, inserisci giro, escludi/includi giro, elenco giri per giocatore e pista).
6. Testo dell'interfaccia in italiano. Verifica che `flutter analyze` e un test base passino.

Vincoli: niente UDP né grafici ora. Dichiara cosa hai provato su emulatore. Fermati e attendi conferma.
