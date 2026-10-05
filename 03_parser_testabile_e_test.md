# PROMPT 03 — Parser separato e test automatici

Leggi `PROGETTO.md` e `server.py`.

Compito:
1. Estrai la logica di parsing e la macchina a stati dei giri in un nuovo `telemetry.py`, senza accesso al database né alla rete: funzioni per header/Session/LapData/CarSetup e una classe di stato per giocatore che, dato un pacchetto, restituisce eventi (nuova sessione, giro completato, aggiornamento live).
2. Fai usare `telemetry.py` a `server.py`, che resta responsabile di socket, database e API. Comportamento identico.
3. Crea `tests/test_telemetry.py` con `unittest` (solo libreria standard) e un generatore di pacchetti sintetici. Casi: giro valido con S1/S2/S3 corretti (esempio: giro 81234 ms, S1 25000, S2 52000 → S3 4234); giro tagliato; out-lap/in-lap scartato; due sessioni diverse; due IP diversi; cambio sessione che azzera lo stato; pacchetto troppo corto o con formato diverso da 2024 ignorato.
4. Esegui i test e riportami l'esito.

Vincoli: nessuna nuova dipendenza. Fermati a fine lavoro e attendi conferma.
