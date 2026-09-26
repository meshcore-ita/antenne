## Come funziona

È una Yagi a 2 elementi: un [dipolo](../guida/#dipolo) alimentato (il tubo da
146 mm) e, dietro, un secondo tubo non alimentato e un po' più lungo (162
mm) chiamato **riflettore**. Il riflettore non è collegato a nulla: la
corrente ci scorre solo per accoppiamento con l'elemento alimentato, con una
fase tale da rispedire in avanti l'energia che altrimenti andrebbe irradiata
all'indietro. Il risultato è più [guadagno](../guida/#guadagno) nella
direzione opposta al riflettore e un [rapporto avanti/dietro](../guida/#avanti-dietro)
misurabile, invece del diagramma quasi uniforme di un dipolo da solo.

Una conseguenza meno intuitiva: l'elemento alimentato (146 mm) è più corto
del dipolo a mezz'onda isolato risonante in un tubo da 6 mm (che si
aggirerebbe sui 160 mm, vedi [Lunghezza d'onda](../guida/#lunghezza-onda)).
Non è un errore di taglio: l'accoppiamento con il riflettore introduce una
reattanza induttiva sull'alimentato, e accorciarlo la compensa
(più dettagli in [Impedenza](../guida/#impedenza)). Per questo l'elemento
"corto" è quello alimentato, non il contrario.

## Misure

| Elemento | Lunghezza | Materiale | Note |
|---|---|---|---|
| Alimentato (driven) | 146 mm | Tubo di rame, 6 mm diametro | Corto apposta per compensare l'accoppiamento col riflettore |
| Riflettore | 162 mm | Tubo di rame, 6 mm diametro | Non alimentato, parassita |
| Distanza alimentato–riflettore | 75 mm (≈ 0,22 λ) | — | — |

Simulazione NEC-2 a 869,618 MHz, spazio libero, polarizzazione verticale:

| Grandezza | Valore |
|---|---|
| [Impedenza](../guida/#impedenza) | 54,4 + j1,7 Ω |
| [ROS](../guida/#ros) su 50 Ω | 1,09 |
| [Guadagno](../guida/#guadagno) | 6,4 dBi (4,2 dBd, vedi [dBi/dBd](../guida/#dbi-dbd)) |
| [Avanti/dietro](../guida/#avanti-dietro) | 8,5 dB (~7× in lineare) |
| ROS minimo | a 864 MHz |

Il ROS di 1,09 è già ottimo così com'è: non serve nessun adattamento
aggiuntivo (vedi la tabella soglie in [ROS](../guida/#ros)).

## Materiali

- Tubo di rame da 6 mm di diametro per entrambi gli elementi.
- Boom in materiale plastico (elettricamente quasi trasparente in RF, non
  richiede correzioni di lunghezza).
- Morsetti di fissaggio degli elementi al boom stampati in 3D/resina.

## Costruzione passo per passo

Non essendo documentati i passaggi esatti seguiti da Fabrizio, ecco una
sequenza **suggerita** e generica per replicare questa antenna, da adattare
ai materiali che hai a disposizione:

1. Taglia i due tubi di rame alle lunghezze della tabella sopra (146 mm e
   162 mm), con un margine di 1–2 mm da rifilare dopo la prova con un
   NanoVNA (vedi [Dal modello alla realtà](../guida/#dal-modello-alla-realta)).
2. Segna sul boom la posizione dei due elementi a 75 mm di distanza, con gli
   elementi montati **verticali** (vedi [Polarizzazione](../guida/#polarizzazione)) e centrati sul boom.
3. Fissa i due tubi ai morsetti passanti per il boom, verificando che ogni
   elemento sia elettricamente isolato dal boom stesso e centrato rispetto
   al punto medio (il centro elettrico deve coincidere con l'asse del
   boom).
4. Collega il cavo coassiale al centro dell'elemento alimentato (il tubo da
   146 mm), tenendo il cavo il più possibile perpendicolare agli elementi
   per un tratto, prima di farlo scendere verso il boom.
5. Monta un balun/choke in ferrite vicino al punto di alimentazione (vedi
   [Adattamento](../guida/#adattamento)) per limitare correnti di modo
   comune sulla calza del cavo.
6. Misura con un NanoVNA prima di installarla definitivamente: se il minimo
   ROS non cade vicino a 869,618 MHz, ritara la lunghezza dell'alimentato a
   piccoli passi.

## Esperimenti da provare

- Prova ad allungare l'elemento alimentato verso la lunghezza di risonanza
  isolata (~160 mm, vedi [Lunghezza d'onda](../guida/#lunghezza-onda)) e
  osserva come cambiano impedenza e ROS: è un modo diretto per "vedere" a
  banco l'effetto dell'accoppiamento descritto sopra.
- Cambia la distanza alimentato-riflettore di qualche centimetro e nota il
  compromesso tra guadagno, rapporto avanti/dietro e impedenza (vedi anche
  l'esperimento di spaziatura sulla scheda della
  [Yagi a 3 elementi di riferimento](../meshcore-ita-yagi-3el/)).
- Se hai un secondo nodo di riferimento, confronta la copertura reale con
  quella di un dipolo semplice montato nello stesso punto: dovresti notare
  più portata nella direzione in cui punta l'antenna, e meno alle spalle.

## Errori comuni

- **Montare il boom con gli elementi orizzontali**: rompe la polarizzazione
  verticale della rete e introduce una forte perdita di
  [polarizzazione incrociata](../guida/#polarizzazione) verso gli altri nodi.
- **Far correre il cavo coassiale parallelo e vicino agli elementi**: può
  accoppiarsi con l'antenna e alterare sia il diagramma sia la lettura del
  ROS rispetto a quanto simulato (vedi
  [Dal modello alla realtà](../guida/#dal-modello-alla-realta)).
- **Ignorare supporti metallici vicini**: un'asta o un palo metallico troppo
  vicino agli elementi si comporta come un parassita non voluto e detiene
  l'antenna.

## Note

- Il file `.nec` è stato trascritto dalla foto dell'originale di Fabrizio,
  non da un file digitale: le misure sono quelle leggibili nella foto.
- Questa antenna è installata sul tetto, verticale, sul nodo solare
  **pybot**. Sotto il boom corre un'asta filettata metallica verticale di
  supporto, e il cavo coassiale passa vicino agli elementi: la simulazione
  qui sopra è in spazio libero, quindi impedenza e diagramma reali possono
  discostarsi leggermente per via di questi due fattori (vedi
  [Dal modello alla realtà](../guida/#dal-modello-alla-realta)).
