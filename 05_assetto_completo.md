# PROMPT 05 — Assetto completo per giro

Leggi `PROGETTO.md`, il parser (`telemetry.py` o `server.py`), `schema.sql` e `static/index.html`.

Compito:
1. Parsa tutti i campi del CarSetup (packetId 5) dell'auto del giocatore, verificando i byte con la specifica ufficiale (50 byte per auto): ali, differenziale/assetto motore, camber, convergenza, sospensioni, barre antirollio, altezze, freni, pressioni gomme, zavorra, carburante. Se non puoi verificare, dichiaralo.
2. Salva l'assetto di ogni giro in una nuova colonna `laps.setup_json` (migrazione sicura) e mantieni `setup_notes` com'è.
3. Nella dashboard aggiungi in ogni riga della tabella un piccolo pulsante "ⓘ" che apre un riquadro con l'assetto di quel giro. Il clic sul resto della riga deve continuare a escludere/includere il giro.
4. Aggiungi la colonna alle API (`/api/laps`) senza rompere i campi esistenti, e un test sintetico.

Vincoli: stile scuro e colori di `PROGETTO.md`. Fermati e attendi conferma.
