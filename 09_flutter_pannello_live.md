# PROMPT 09 — App Flutter: pannello Live · Settori

Leggi `PROGETTO.md` (Pannello Live e Colori settore) e il codice già presente in `app/`.

Compito:
1. Schermata Live per il giocatore selezionato, alimentata dallo stream live del Prompt 07, con aggiornamento almeno 1 volta al secondo.
2. Riga info "Sessione · Giro N · tempo corrente (m:ss.mmm)" e "· GIRO TAGLIATO" se invalido.
3. Tre riquadri S1/S2/S3 con bordo e testo colorati: viola = ≤ miglior settore, verde = ≤ media degli ultimi 10, giallo = più lento. Riferimento: solo giri validi non esclusi dello **stesso gruppo di sessione** del live. S3 mostra "in corso" finché il giro non finisce.
4. Senza dati: "In attesa di dati dal gioco…". Con la schermata Live aperta lo schermo resta acceso (`wakelock_plus`).
5. Test della funzione dei colori con casi di esempio.

Vincoli: stile del tema esistente. Fermati e attendi conferma.
