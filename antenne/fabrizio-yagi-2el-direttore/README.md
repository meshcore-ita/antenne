## Come funziona

Variante della [Yagi a 2 elementi con riflettore](../fabrizio-yagi-2el-riflettore/):
qui l'elemento parassita non è dietro ma **davanti** all'alimentato, ed è più
corto invece che più lungo. Un elemento parassita più corto del
[dipolo](../guida/#dipolo) risonante si comporta da **direttore**: la
corrente indotta ha la fase giusta per spingere l'irradiazione in avanti,
verso di lui, invece di rimandarla indietro come fa un riflettore.

Il risultato tipico di un direttore singolo, rispetto a un riflettore
singolo, è un [guadagno](../guida/#guadagno) leggermente inferiore (qui 5,3
dBi contro i 6,4 dBi della versione con riflettore) a parità di
configurazione a 2 elementi, ma un adattamento di
[impedenza](../guida/#impedenza) spesso più comodo: qui l'alimentato (165
mm) resta molto più vicino alla lunghezza di risonanza isolata di un tubo
sottile, e l'impedenza simulata (50,3 − j1,0 Ω) cade quasi esattamente su 50
Ω.

## Misure

| Elemento | Lunghezza | Materiale | Note |
|---|---|---|---|
| Alimentato (driven) | 165 mm | Tondino/tubo, 3 mm diametro | — |
| Direttore | 140 mm | Tondino/tubo, 3 mm diametro | Non alimentato, parassita, davanti all'alimentato |
| Distanza alimentato–direttore | 44 mm (≈ 0,13 λ) | — | Più stretta della spaziatura riflettore-alimentato dell'altra variante |

Simulazione NEC-2 a 869,618 MHz, spazio libero, polarizzazione verticale:

| Grandezza | Valore |
|---|---|
| [Impedenza](../guida/#impedenza) | 50,3 − j1,0 Ω |
| [ROS](../guida/#ros) su 50 Ω | 1,02 |
| [Guadagno](../guida/#guadagno) | 5,3 dBi (3,1 dBd, vedi [dBi/dBd](../guida/#dbi-dbd)) |
| [Avanti/dietro](../guida/#avanti-dietro) | 8,1 dB (~6,5× in lineare) |
| ROS minimo | a 871 MHz |

## Esperimenti da provare

- Confronta direttamente questa scheda con la
  [versione con riflettore](../fabrizio-yagi-2el-riflettore/): stessa idea
  (2 elementi, uno parassita), posizione e lunghezza del parassita
  invertite. È un buon modo per "sentire sulla propria pelle" la differenza
  tra direttore e riflettore descritta in "Come funziona" qui sopra.
- Prova ad accorciare ulteriormente il direttore di qualche millimetro: il
  guadagno in avanti dovrebbe aumentare leggermente, ma la banda utile (il
  range di frequenza a basso ROS) si restringe — un compromesso comune nel
  progettare Yagi con più elementi, come si vede in modo più estremo nella
  [Yagi a 10 elementi](../fabrizio-yagi-10el/).
- Combina riflettore e direttore nello stesso modello (3 elementi): è
  esattamente l'idea della
  [Yagi a 3 elementi di riferimento](../meshcore-ita-yagi-3el/) di questa
  galleria.

## Errori comuni

- **Montare gli elementi orizzontali**: come per ogni antenna di questa
  galleria, rompe la [polarizzazione verticale](../guida/#polarizzazione)
  usata dalla rete MeshCore ITA.
- **Confondere direttore e riflettore per posizione senza controllare la
  lunghezza**: quello che conta elettricamente è che il direttore sia più
  corto dell'alimentato e il riflettore più lungo, non solo la posizione sul
  boom.

## Note

Variante di studio, non installata su un nodo reale: nessuna foto
disponibile. Misure trascritte dal file NEC originale di Fabrizio.
