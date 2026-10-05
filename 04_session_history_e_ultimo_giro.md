# PROMPT 04 — Session History (id 11) e salvataggio dell'ultimo giro

Leggi `PROGETTO.md`, `telemetry.py` (se esiste, altrimenti `server.py`) e `schema.sql`.

Compito:
1. Aggiungi il parsing del pacchetto Session History (packetId 11) per l'auto del giocatore. Struttura da verificare con la specifica ufficiale: dopo l'header, 7 campi u8 (carIdx, numLaps, numTyreStints, bestLapTimeLapNum, bestSector1/2/3LapNum), poi 100 voci da 14 byte (lapTimeInMS u32, s1 msPart u16, s1 minutesPart u8, s2 msPart u16, s2 minutesPart u8, s3 msPart u16, s3 minutesPart u8, lapValidBitFlags u8), poi 8 stint gomme. Se non riesci a verificare, dichiaralo.
2. Usa questi dati per riconciliare i giri: tempo e settori esatti, validità dai bitflag, e salvataggio dell'**ultimo giro** a fine sessione, che oggi può andare perso.
3. Evita i duplicati: indice UNIQUE su `laps(session_id, lap_number)` con upsert che aggiorna tempi e validità ma **conserva il valore di `excluded`**. Migrazione sicura per i database esistenti.
4. Il flusso attuale (LapData) deve continuare a funzionare se Session History non arriva.
5. Aggiungi test sintetici per il nuovo pacchetto e per l'upsert.

Vincoli: stesse API e stesso comportamento della dashboard. Fermati e attendi conferma.
