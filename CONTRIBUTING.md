# Aggiungere un'antenna

1. Crea una cartella `antenne/<autore>-<tipo>`, in minuscolo con trattini.
2. Metti il modello in `antenna.nec`. Misure in metri; puoi usare variabili
   `SY` come in 4nec2. Schede supportate: `CM CE SY GW GS GE EK GN EX LD FR`
   (`RP`, `PT`, `EN` vengono ignorate: il diagramma lo calcola la galleria).

   La galleria mostra il file riga per riga, quindi i commenti contano. Per
   restare coerente con gli altri modelli:
   - in testa, righe `CM` che dicono cos'è l'antenna, le misure principali,
     su quale asse stanno elementi e boom, materiale e diametro, dove è
     alimentata e i valori simulati a 869.618 MHz; poi `CE` da solo;
   - un `SY` per riga, in metri scritti come `mm/1000`, con un commento
     `'` dopo un TAB; il diametro in `dia` e nel `GW` il raggio `dia/2`;
   - commenti `'` su una riga propria sopra ogni `GW`, `EX`, `FR`;
   - ordine `GE 0`, `LD`, `GN -1`, `EK`, `EX`, `FR`, `RP`, `EN`; campi
     separati da spazi; fili numerati 1..N; `EX` sul segmento centrale;
   - nei `.nec` solo caratteri ASCII (`e'`, `ohm`, `gradi`): 4nec2 non
     legge bene gli accenti.

   Un esempio completo è `antenne/fabrizio-yagi-lfa-3el/antenna.nec`.

3. Aggiungi `meta.json`:

   ```json
   {
     "title": "Dipolo verticale 869 MHz",
     "author": "Nome o nominativo",
     "type": "Dipolo a mezz'onda",
     "status": "In uso | Prototipo | Variante di studio",
     "description": "Una o due frasi su misure e materiali.",
     "photos": [{ "file": "foto.jpg", "alt": "Descrizione della foto" }],
     "license": "CC-BY-SA-4.0",
     "montaggio": "Verticale"
   }
   ```

   `montaggio` è facoltativo: indicalo se l'antenna reale è montata ruotata
   rispetto al file (per esempio elementi lungo y nel modello ma verticali sul
   tetto). La galleria mostra allora la polarizzazione reale.

4. Facoltativo: `README.md` con note di costruzione, foto, e una misura
   `.s1p` fatta con un VNA.
5. Controlla in locale con `python tools/build.py` e apri una pull request.

Pubblicando confermi che il modello e le foto sono tuoi, o che hai il
permesso dell'autore, e che li rilasci con la licenza indicata.
