# PROGETTO — Telemetria e analisi prestazioni F1 24 (specifica di riferimento)

Questo file è la specifica del sistema esistente. Il codice è nella stessa cartella: `server.py`, `schema.sql`, `static/` (dashboard + PWA). Il comportamento descritto qui è quello da preservare. Tutta l'interfaccia è in **italiano**.

**Stato:** testato SOLO con pacchetti UDP sintetici. NON verificato con il gioco reale né su dispositivi mobili. Dichiara sempre cosa hai verificato davvero e cosa solo in simulazione.

## Architettura
F1 24 → UDP porta 20777 → `server.py` (un thread listener, uno stato per IP) → SQLite `f1telemetry.db` + API HTTP :8000 + file statici. La dashboard fa polling (live 1 s, resto 5 s). Nessuna autenticazione (LAN).

## Protocollo UDP F1 24 (little-endian, accettato solo se packetFormat == 2024)
- **Header 29 byte**, `"<HBBBBBQfIIBB"`: 0 packetFormat, 1 gameYear, 2 major, 3 minor, 4 packetVersion, 5 **packetId**, 6 **sessionUID**, 7 sessionTime, 8 frameId, 9 overallFrameId, 10 **playerCarIndex**, 11 secondaryPlayerCarIndex.
- Packet id: 0 Motion, 1 Session, 2 LapData, 3 Event, 4 Participants, 5 CarSetups, 6 CarTelemetry, 7 CarStatus, 8 FinalClassification, 9 LobbyInfo, 10 CarDamage, 11 SessionHistory, 12 TyreSets, 13 MotionEx, 14 TimeTrial. Usati ora: 1, 2, 5.
- **Session (id 1)**, da byte 29, `"<BbbBHBb"`: weather, trackTemp, airTemp, totalLaps, trackLength(m), sessionType, trackId. weather: 0 Sereno, 1 Poco nuvoloso, 2 Coperto, 3 Pioggia leggera, 4 Pioggia forte, 5 Temporale. sessionType: 1-3 Prove 1/2/3, 4 Prove brevi, 5/6/7 Qualifica 1/2/3, 8 Qualifica breve, 9 Qualifica OSQ, 10/11/12 Gara/Gara 2/Gara 3, 13 Time Trial. Piste: dizionario `TRACKS` in `server.py` (mancano 8, 21-25, 28).
- **LapData (id 2)**: 22 auto × 57 byte da byte 29 (+2 byte finali); pacchetto atteso ≈ 1285 byte. Si legge solo l'auto del giocatore: offset `29 + playerCarIndex*57`, struct `"<IIHBHBHBHBfff" + "B"*15 + "HHB" + "fB"`. Indici: 0 lastLapTimeMs, 1 currentLapTimeMs, 2 s1 msPart, 3 s1 minutesPart, 4 s2 msPart, 5 s2 minutesPart, 6-9 delta, 10-12 distanze, 13 carPosition, **14 currentLapNum**, **15 pitStatus**, 16 numPitStops, **17 sector (0=S1,1=S2,2=S3)**, **18 currentLapInvalid**, 19 penalties, 20 totalWarnings, 21 cornerCuttingWarnings, 22-23 pene da scontare, 24 gridPosition, 25 driverStatus, 26 resultStatus, 27-30 pit lane, 31 speedTrapFastestSpeed, 32 speedTrapFastestLap. Tempo settore = msPart + minutesPart*60000. **S3 = tempoGiro − S1 − S2** (non arriva dal gioco).
- **CarSetups (id 5)**: 22 × 50 byte da byte 29 (≈1133 byte totali). Oggi si leggono solo i primi 2 byte dell'auto del giocatore (ala ant., ala post.) salvati come testo in `laps.setup_notes`.

## Logica dei giri (stato per IP)
1. Primo pacchetto valido da un IP → crea `users(ip, nome=ip)` e lo stato in memoria.
2. Pacchetto Session con `sessionUID` nuovo → crea `circuits`/`sessions` (INSERT OR IGNORE), azzera i contatori. Senza Session i LapData sono ignorati.
3. LapData: se `currentLapNum` cambia, salva il giro appena finito con `lastLapTimeMs` solo se numero giro precedente > 0, lastLapTimeMs > 0 e (con `SKIP_PIT_LAPS`) `pitStatus` non è mai stato ≠ 0 durante il giro. Poi azzera s1, s2, invalid, pit.
4. Durante il giro: `sector>=1` memorizza S1; `sector>=2` memorizza S2; `currentLapInvalid==1` in qualsiasi pacchetto rende il giro non valido; `pitStatus!=0` segna il giro "con pit".
5. Giro non valido → `is_valid=0`; salvato se `SAVE_INVALID=True`. `excluded` parte da 0.
6. A ogni LapData si aggiorna lo stato **live** del giocatore: pista, tipo sessione, giro, settore, tempo corrente, S1, S2, invalid.
Limiti noti: l'ultimo giro di una sessione può non essere salvato; il giro 1 di gara include la partenza da fermo.

## Database (`schema.sql`)
`users(id, ip UNIQUE, nome)` · `circuits(id=trackId, nome, paese, lunghezza, record_personale[non usato])` · `sessions(id, session_uid UNIQUE, data, circuit_id, tipo_sessione, meteo, user_id)` · `laps(id, session_id, lap_number, lap_time_ms, sector_1_ms, sector_2_ms, sector_3_ms, is_valid, setup_notes, excluded DEFAULT 0)`. `init_db()` fa anche `ALTER TABLE` per vecchi DB.

## API
`GET /api/users` · `GET /api/circuits?user=` · `GET /api/laps?circuit=&user=` (tutti i giri, anche non validi/esclusi) · `GET /api/live?user=` · `POST /api/user {id,nome}` (max 30 car.) · `POST /api/lap {id,excluded}`.

## Dashboard (regole esatte)
- **Selettori:** giocatore (+ ✎ rinomina), circuito, filtro sessione: Tutte / Gara (race pace) / Time Trial / Prove libere / Qualifica 1 / 2 / 3. Gruppi: "Time Trial"→tt, "Prove…"→pl, "Qualifica 1/2/3"→q1/q2/q3, "Gara…"→race, altro→other (solo in "Tutte").
- **Insieme `ok`:** giri del filtro con `is_valid=1`, `excluded=0` e, con filtro Gara, `lap_number != 1`.
- **KPI:** PB = min tempo di `ok`. Ideal Lap = min S1 + min S2 + min S3 (solo giri con 3 settori); mostrare PB−Ideal in secondi. Media = media degli ultimi 10 di `ok` (titolo "Race pace (ultimi 10 giri)" con filtro Gara). Consistenza = deviazione standard di popolazione degli ultimi 10, mostrata ±s (≥2 giri).
- **Grafico:** linea dei tempi di `ok`, linea tratteggiata gialla del PB, punti colorati per sessione (gara #E10600, TT #FCD116, prove #38bdf8, Q1 #a78bfa, Q2 #c084fc, Q3 #e879f9, altro #8E95A5).
- **Feedback (4 regole):** (1) con ≥3 giri completi di settori negli ultimi 10: settore con perdita media massima rispetto al suo miglior settore; (2) con ≥3 giri: std <0.2 s alta, <0.5 s discreta, altrimenti bassa; (3) con ≥8 giri: media ultimi 5 vs 5 precedenti (trend positivo / peggioramento); (4) margine PB−Ideal. Senza dati: "Servono almeno 3 giri validi."
- **Tabella:** ultimi 12 giri del filtro (inclusi non validi/esclusi), più recenti in alto: #, tempo, S1, S2, S3, badge Valido (verde)/Tagliato (rosso), sessione colorata. **Colori settore:** viola #a855f7 = ≤ miglior settore di `ok`; verde #22c55e = ≤ media dei settori degli ultimi 10 di `ok`; giallo #FCD116 = più lento. **Clic/tocco su un giro = esclude/include** (riga grigia #555 e barrata, tolto da tutte le statistiche).
- **Pannello Live:** riquadri S1/S2/S3 colorati con la stessa regola, confrontati solo con giri validi non esclusi dello stesso gruppo di sessione; riga info "Sessione · Giro N · tempo corrente" (+ "· GIRO TAGLIATO"); S3 resta "in corso" fino a fine giro; senza dati "In attesa di dati dal gioco…".

## Design
Sfondo #0B0E14, card #151922, bordi #262B38, rosso #E10600, giallo #FCD116, testo #FFFFFF, secondario #8E95A5, ok #22c55e. Font Teko (titoli/KPI, 700 corsivo) e Titillium Web (testo). Tema scuro motorsport, raggio card 8 px.

## Impostazioni gioco (F1 24 → Impostazioni telemetria)
UDP Telemetry On · Broadcast Off · IP = dispositivo/PC che riceve · Porta 20777 · 20 Hz · Formato 2024 · Your Telemetry Public.
