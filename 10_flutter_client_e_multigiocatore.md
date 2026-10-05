# PROMPT 10 — App Flutter: modalità client e multi-giocatore

Leggi `PROGETTO.md` (API) e il codice già presente in `app/`.

Compito:
1. Introduci un'interfaccia di repository con due implementazioni: **Locale** (database sul dispositivo, modalità standalone) e **Remota** (chiama le API di `server.py`: `/api/users`, `/api/circuits`, `/api/laps`, `/api/live`, `POST /api/user`, `POST /api/lap`).
2. Nelle Impostazioni: scelta modalità (Standalone / Client), campo URL del server (es. `http://192.168.1.25:8000`) con pulsante "Prova connessione".
3. L'interfaccia (Dashboard, Giri, Live) deve funzionare in modo identico con entrambi i repository. In modalità Client il polling è: live ogni 1 s, resto ogni 5 s.
4. Gestisci errori di rete con messaggi chiari in italiano (server non raggiungibile, timeout) senza far crollare l'app.
5. Multi-giocatore: ogni IP è un giocatore, nome iniziale uguale all'IP, rinominabile; nuovi giocatori compaiono da soli nel selettore.

Vincoli: nessuna modifica a `server.py` salvo bug trovati (segnalali). Fermati e attendi conferma.
