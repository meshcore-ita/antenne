# Aggiungere un'antenna

1. Crea una cartella `antenne/<autore>-<tipo>`, in minuscolo con trattini.
2. Metti il modello in `antenna.nec`. Misure in metri; puoi usare variabili
   `SY` come in 4nec2. Schede supportate: `CM CE SY GW GS GE EK GN EX LD FR`
   (`RP`, `PT`, `EN` vengono ignorate: il diagramma lo calcola la galleria).
3. Aggiungi `meta.json`:

   ```json
   {
     "title": "Dipolo verticale 869 MHz",
     "author": "Nome o nominativo",
     "type": "Dipolo a mezz'onda",
     "status": "In uso | Prototipo | Variante di studio",
     "description": "Una o due frasi su misure e materiali.",
     "photos": [{ "file": "foto.jpg", "alt": "Descrizione della foto" }],
     "license": "CC-BY-SA-4.0"
   }
   ```

4. Facoltativo: `README.md` con note di costruzione, foto, e una misura
   `.s1p` fatta con un VNA.
5. Controlla in locale con `python tools/build.py` e apri una pull request.

Pubblicando confermi che il modello e le foto sono tuoi, o che hai il
permesso dell'autore, e che li rilasci con la licenza indicata.
