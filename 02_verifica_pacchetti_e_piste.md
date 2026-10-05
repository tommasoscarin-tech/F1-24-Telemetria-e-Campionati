# PROMPT 02 — Verifica pacchetti UDP e completamento piste

Leggi `PROGETTO.md` (sezione Protocollo UDP) e `server.py`.

Compito:
1. Se hai accesso al web, cerca la specifica ufficiale "Data Output from F1 24" e confronta: header (29 byte), Session, LapData (57 byte per auto), CarSetups (50 byte). Se non puoi verificare, dillo e non inventare.
2. Correggi in `server.py` eventuali struct/offset sbagliati, spiegando ogni correzione.
3. Aggiungi, al primo arrivo di ogni `packetId`, una riga di log con `packetId` e `len(d)` (una sola volta per id e per IP), per poter controllare le dimensioni col gioco reale.
4. Completa `TRACKS` con tutte le piste di F1 24 (mancano 8, 21-25, 28) e salva anche il paese in `circuits.paese`.

Vincoli: non cambiare il comportamento descritto in `PROGETTO.md`, API e schema restano compatibili. Riesegui l'avvio per controllare che non ci siano errori. Elenca cosa è verificato e cosa no, poi fermati.
