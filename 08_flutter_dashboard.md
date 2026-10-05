# PROMPT 08 — App Flutter: dashboard (KPI, grafico, feedback, tabella)

Leggi `PROGETTO.md` (sezione Dashboard) e `static/index.html` come riferimento del comportamento. Lavora in `app/`.

Compito:
1. Crea `stats.dart` (Dart puro, senza UI) con le formule **identiche** alla dashboard web: insieme `ok`, PB, Ideal Lap, media ultimi 10 (race pace con filtro Gara), deviazione standard di popolazione, regole del feedback con le stesse soglie, gruppi di sessione. Aggiungi test unitari con dati di esempio.
2. Schermata Dashboard: selettore giocatore con rinomina, selettore circuito, filtro sessione (Tutte, Gara, Time Trial, Prove libere, Q1, Q2, Q3), 3 card KPI, grafico con `fl_chart` (linea tempi, PB tratteggiato giallo, punti colorati per sessione), riquadro feedback.
3. Schermata Giri: tabella degli ultimi giri con tempi, S1/S2/S3 colorati (viola/verde/giallo come in `PROGETTO.md`), badge Valido/Tagliato, sessione colorata, e **tocco su un giro = esclude/include** (riga grigia e barrata, tolto da tutte le statistiche).
4. I dati si aggiornano da soli quando arrivano nuovi giri.

Vincoli: colori e font di `PROGETTO.md`, testi in italiano. Fermati e attendi conferma.
