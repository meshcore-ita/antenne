## Come funziona

Una Yagi con **10 elementi** (1 riflettore, 1 alimentato, 8 direttori in
fila) è la stessa idea della [Yagi a 2 elementi](../fabrizio-yagi-2el-riflettore/)
o della [Yagi a 3 elementi di riferimento](../meshcore-ita-yagi-3el/) di
questa galleria, spinta molto più in là: più elementi parassiti in fila
restringono il [diagramma di irradiazione](../guida/#diagramma) e alzano il
[guadagno](../guida/#guadagno) e il [rapporto avanti/dietro](../guida/#avanti-dietro)
molto oltre quello che si ottiene con 2-3 elementi, a prezzo di un boom
lungo (qui circa 58 cm) e di un puntamento più critico.

Questo file è particolare: è il progetto originale tedesco per **432 MHz**,
non pensato per MeshCore, riscalato a 869 MHz con una variabile
`fa = 432/868`. È un ottimo caso di studio proprio perché lo scalamento non è
perfetto: il file scala le **lunghezze** degli elementi per `fa`, ma **non i
raggi** (restano quelli pensati per 432 MHz). Come spiegato in
[Lunghezza d'onda](../guida/#lunghezza-onda), a parità di lunghezza un filo
più spesso è elettricamente più lungo (risuona a una lunghezza fisica più
corta). Il tondino da 5 mm di diametro, scelto per 432 MHz, a 869 MHz è in
proporzione spesso il doppio: per restare fedeli al progetto servirebbero
circa 2,5 mm. I "fili" sono quindi relativamente più spessi del previsto,
non più sottili. Il risultato è una reattanza residua induttiva
sull'alimentato e una risonanza spostata più in basso in frequenza (ROS
minimo attorno a 855 MHz) invece di un'impedenza pulita a 869,618 MHz.

## Misure

Progetto originale a 432 MHz, elementi in alluminio, riscalato con
`fa = 432 / 868 ≈ 0,4977`. Boom totale di circa 583 mm.

| Elemento | Lunghezza (869 MHz) |
|---|---|
| Riflettore | 174 mm |
| Alimentato (driven) | 153 mm |
| Direttori 1–8 | da 146 a 114 mm, decrescenti verso la punta del boom |

Simulazione NEC-2 a 869,618 MHz, spazio libero, con perdita per
conducibilità reale dell'alluminio inclusa nel modello (carta `LD`):

| Grandezza | Valore |
|---|---|
| [Impedenza](../guida/#impedenza) | 33,2 + j18,1 Ω |
| [ROS](../guida/#ros) su 50 Ω | 1,82 |
| [Guadagno](../guida/#guadagno) | 12,5 dBi (10,3 dBd, vedi [dBi/dBd](../guida/#dbi-dbd)) |
| [Avanti/dietro](../guida/#avanti-dietro) | 22,3 dB (~170× in lineare) |
| ROS minimo | a 855 MHz (fuori sotto-banda) |

Un ROS di 1,82 è ancora sotto la soglia critica di 3 (vedi la tabella in
[ROS](../guida/#ros)), ma è il valore più alto di tutta questa galleria
(le altre arrivano al massimo a 1,44), quasi
interamente per via della X = +18,1 Ω non compensata: senza quella
reattanza il ROS sarebbe molto più vicino a 1.

## Materiali

Elementi in alluminio (come da progetto originale), boom non specificato nel
file.

## Esperimenti da provare

- Il file stesso lo segnala nei commenti: il progetto compensa un **boom
  metallico** con correzioni fisse di +6 mm su ogni elemento parassita e
  +12 mm sull'alimentato. Prova a rimuovere queste correzioni (o ad
  applicarle diversamente) e osserva quanto si sposta l'impedenza — un
  esempio concreto di quanto discusso in
  [Dal modello alla realtà](../guida/#dal-modello-alla-realta).
- Per avvicinare l'impedenza a 50 + j0 Ω restando fedeli a questo progetto,
  ci sono due strade equivalenti a quanto descritto in
  [Adattamento](../guida/#adattamento): accorciare l'alimentato di qualche
  millimetro (cancella parte della X induttiva, come nel caso della
  [Yagi a 3 elementi](../meshcore-ita-yagi-3el/)), oppure scalare anche i
  raggi degli elementi per `fa` insieme alle lunghezze, così da restare
  fedeli alle proporzioni originali pensate per 432 MHz.
- Con un condensatore in serie da circa 10,1 pF a 869,618 MHz si cancella
  quasi del tutto la X = +18,1 Ω simulata, lasciando solo il disadattamento
  di R (33,2 Ω verso 50 Ω) da sistemare con un trasformatore a λ/4 o una
  rete a L (vedi [Adattamento](../guida/#adattamento)).
- Scalando anche i raggi per `fa` (diametro circa 2,5 mm sugli elementi e
  7 mm sull'alimentato) si resta fedeli alle proporzioni originali a
  432 MHz: in simulazione questo porta a Z ≈ 43 + j5 Ω, ROS ≈ 1,20,
  guadagno ≈ 11,4 dBi e avanti/dietro ≈ 20 dB.

## Errori comuni

- **Copiare le misure senza notare la mancata scalatura dei raggi**: è
  proprio la particolarità (e il limite) di questo file, spiegata sopra in
  "Come funziona": in breve, non aspettarti un adattamento pulito a 50 Ω
  senza ritarare.
- **Montare 10 elementi senza un boom rigido**: con un boom così lungo (58
  cm) e molti elementi, un minimo disallineamento o una flessione del boom
  sposta più impedenza e diagramma rispetto a una Yagi corta a 2-3 elementi.

## Note

- Il file scala le lunghezze ma **non i diametri**, che restano quelli
  dell'originale a 432 MHz. Per questo l'adattamento a 869 MHz non è
  centrato: va accorciato l'alimentato o scalati anche i raggi.
- I commenti originali, in tedesco, indicano correzioni per il boom
  metallico (+6 mm sugli elementi, +12 mm sull'alimentato).
