# Antenne MeshCore ITA

Modelli NEC-2 di antenne per MeshCore condivisi dalla community italiana,
simulati automaticamente a **869,618 MHz** (preset italiano) e pubblicati come
galleria statica.

Ogni antenna ha una cartella in `antenne/`:

```
antenne/<autore>-<tipo>/
  antenna.nec   modello NEC-2 (schede di testo, variabili SY ammesse)
  meta.json     titolo, autore, tipo, stato, descrizione, foto, licenza
  README.md     note libere: costruzione, materiali, installazione, misure
  *.jpg|*.png   foto (facoltative)
  *.s1p         misura reale con VNA (facoltativa)
```

## Cosa calcola la galleria

Per ogni modello, in spazio libero o sopra il terreno definito dal file:

- impedenza e ROS su 50 Ω a 869,618 MHz, e il ROS da 855 a 885 MHz
- guadagno massimo e rapporto avanti/dietro
- due tagli del diagramma di irradiazione attraverso la direzione di massimo

Ogni scheda ha anche una vista 3D interattiva (diagramma di irradiazione e
geometria) fatta con [three.js](https://threejs.org/), incluso nel repo in
`tools/vendor/three/` insieme ai font: la galleria non carica nulla da
servizi esterni. I file `.nec` si aprono anche con xnec2c, 4nec2 o EZNEC.

## Generare la galleria in locale

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python tools/build.py      # scrive site/
python -m http.server -d site
```

Il build fallisce se un modello usa schede non supportate o contiene errori.

## Contribuire

Vedi [CONTRIBUTING.md](CONTRIBUTING.md).

## Licenze

- Modelli, foto e testi in `antenne/`: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/),
  salvo diversa indicazione in `meta.json`. Ogni autore conferma di poterli
  condividere.
- Codice in `tools/`: MIT, vedi [LICENSE](LICENSE).
