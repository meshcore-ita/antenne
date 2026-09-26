# Guida: capire un'antenna prima di costruirla

Questa guida spiega, con parole semplici e numeri veri, i concetti che servono
per leggere le schede di questa galleria e costruire una prima antenna per
MeshCore sul preset italiano **869,618 MHz** (sotto-banda 869,4–869,65 MHz,
limite 500 mW ERP, duty cycle 10%). Ogni termine tecnico è spiegato la prima
volta che compare. Tutti i numeri sono calcolati o presi dalle simulazioni
NEC-2 di questo repository, non a occhio: dove serve, la formula usata è
scritta accanto al risultato.

## Lunghezza d'onda, λ/2 e λ/4 {#lunghezza-onda}

La **lunghezza d'onda** (si scrive con la lettera greca λ, "lambda") è la
distanza percorsa da un'onda radio in un periodo. Si calcola con

```
λ = c / f
```

dove *c* è la velocità della luce (299 792 458 m/s) e *f* la frequenza. Al
preset italiano:

```
λ = 299 792 458 / 869 618 000 ≈ 0,34474 m = 344,74 mm
```

Le antenne a filo si progettano quasi sempre come frazioni di λ:

| Frazione | Lunghezza teorica |
|---|---|
| λ/2 (mezz'onda, il dipolo) | 172,37 mm |
| λ/4 (quarto d'onda, lo stilo di una ground plane) | 86,19 mm |

Questi sono i numeri **teorici**, validi per un filo infinitamente sottile nel
vuoto. Un filo vero ha uno spessore, e questo cambia due cose: aggiunge un
po' di capacità alle estremità ("effetto di estremità") e modifica la
velocità con cui l'onda si muove lungo il conduttore. Il risultato pratico è
che l'antenna risuona (cioè la reattanza X si annulla, vedi
[Impedenza](#impedenza)) a una lunghezza **più corta** di quella teorica, e
più il filo è spesso rispetto alla lunghezza, più l'accorciamento è
marcato.

Non è una regola fissa da manuale: lo verifichiamo simulando. Il modello
`meshcore-ita-dipolo` di questa galleria è un dipolo dritto in filo di rame da
2 mm di diametro; simulato in NEC-2, risuona a **160,6 mm** totali invece dei
172,37 mm teorici: **6,8% più corto**. Il modello `meshcore-ita-ground-plane`
ha uno stilo da 2 mm con 4 radiali inclinati a 45°; risuona a **77,5 mm**
invece di 86,19 mm teorici: **10,1% più corto** (qui l'accorciamento include
anche l'effetto dei radiali vicini, non solo lo spessore del filo).

**In pratica:** taglia sempre il filo un po' più lungo del teorico, poi
misura (con un NanoVNA, vedi [Dal modello alla realtà](#dal-modello-alla-realta))
o simula, e accorcia a piccoli passi (pochi millimetri per volta):
accorciare sposta la risonanza verso l'alto in frequenza, allungare la sposta
verso il basso.

## Il dipolo {#dipolo}

Il **dipolo a mezz'onda** è l'antenna più semplice ed è il mattone di quasi
tutte le altre (una Yagi è un dipolo con elementi parassiti aggiunti
accanto). È fatto da due bracci allineati, ciascuno lungo circa λ/4, con un
piccolo distacco al centro dove si collega il cavo: un braccio va al
conduttore centrale del coassiale, l'altro alla calza.

Lungo il dipolo la corrente è massima al centro (dove si alimenta) e scende a
zero alle punte; la tensione fa il contrario, minima al centro e massima alle
punte. Per questo il centro è il punto a **bassa impedenza** (dove si
alimenta comodamente) e le punte sono ad **alta impedenza** (non ci si
collega un cavo lì).

Il dipolo a mezz'onda in filo sottile, nel vuoto, ha un'impedenza teorica di
riferimento di circa 73 Ω. Il nostro modello `meshcore-ita-dipolo` (filo da 2
mm, lunghezza tarata 160,6 mm) simula **71,9 − j0,1 Ω**: molto vicino al
valore teorico, con un residuo di reattanza (spiegato in
[Impedenza](#impedenza)) praticamente nullo.

Negli elementi delle Yagi di questa galleria l'elemento alimentato è sempre
una variante del dipolo, ma quasi mai lungo esattamente come un dipolo
isolato: gli elementi parassiti vicini (riflettore, direttore) si accoppiano
con lui e ne spostano l'impedenza, quindi va ritarato in lunghezza — se ne
parla in dettaglio in [Impedenza](#impedenza) e nella scheda della Yagi a 3
elementi.

## Polarizzazione {#polarizzazione}

La **polarizzazione** è la direzione in cui oscilla il campo elettrico
irradiato. Un'antenna a filo dritto irradia con polarizzazione parallela al
filo: un dipolo montato **verticale** irradia (e riceve meglio) campo
**verticale**; montato orizzontale, campo orizzontale.

La rete MeshCore ITA usa **polarizzazione verticale** in modo coerente su
tutti i nodi, perché la maggior parte dei dispositivi (portatili, nodi da
zaino, stilo su un palo) è naturalmente verticale. Per questo tutte le
antenne di questa galleria — comprese le Yagi di Fabrizio — montano gli
elementi verticali, anche quando il boom è orizzontale.

Perché è importante: due antenne con polarizzazioni incrociate (una
verticale, una orizzontale) si accoppiano molto male. In teoria, per due
antenne perfettamente allineate e in vuoto, la perdita sarebbe infinita
(polarizzazioni ortogonali = zero accoppiamento); nella pratica, con
riflessioni e percorsi multipli dell'onda radio in un ambiente reale, si
misurano tipicamente **20 dB o più** di perdita da polarizzazione incrociata
— cioè il segnale utile scende a un centesimo (20 dB = fattore 100) o meno.
È una delle cause più comuni di "non lo sento" quando un nodo è montato
storto: prima di cercare altre spiegazioni, controlla che l'antenna sia
verticale come quella dell'altro capo del collegamento. Per come questo si
riflette sulla portata attesa, vedi la pagina
[link budget](https://meshcore-ita.github.io/link-budget/).

## dBi e dBd {#dbi-dbd}

Il guadagno di un'antenna si esprime sempre **rispetto a un riferimento**,
perché da solo un'antenna non crea energia (vedi [Guadagno](#guadagno)). Ci
sono due riferimenti comuni:

- **dBi**: rispetto a un'antenna isotropica ideale, che irradia identica in
  ogni direzione (non esiste in pratica, è un riferimento matematico).
- **dBd**: rispetto a un dipolo a mezz'onda reale, che già di suo concentra
  un po' di energia (non irradia sulle proprie punte).

Un dipolo a mezz'onda ha una direttività nota per via teorica di 1,64 volte
un'isotropica, cioè `10·log₁₀(1,64) = 2,15 dB`. Da qui la conversione fissa:

```
guadagno in dBi = guadagno in dBd + 2,15
```

Le simulazioni di questa galleria (e tutti i numeri "guadagno dBi" mostrati
nelle schede) sono sempre in **dBi**, perché è quello che calcola
direttamente NEC-2. Quando una legge o un datasheet parla di ERP (vedi
[ERP](#erp)) il riferimento è invece il dipolo, quindi in dBd: ricorda di
togliere 2,15 dB prima di usare quella formula.

| Antenna (di questa galleria) | Guadagno dBi | Guadagno dBd |
|---|---|---|
| Dipolo di riferimento | 2,13 | −0,02 |
| Ground plane di riferimento | 2,24 | 0,09 |
| Yagi 3 elementi di riferimento | 8,05 | 5,90 |
| Yagi 2 el. con riflettore (Fabrizio) | 6,36 | 4,21 |
| Yagi 2 el. con direttore (Fabrizio) | 5,28 | 3,13 |
| Yagi 10 elementi (Fabrizio) | 12,45 | 10,30 |

Nota che il dipolo e la ground plane, i due riferimenti "senza guadagno",
cadono giustamente vicino a **0 dBd**: per definizione un dipolo reale ha
guadagno ~0 dBd rispetto a sé stesso.

## Il guadagno non è amplificazione {#guadagno}

Un errore comune da principianti: pensare che un'antenna a "più dBi" renda il
segnale più forte in senso assoluto, come farebbe un amplificatore. Non è
così: un'antenna passiva non aggiunge energia. La potenza totale irradiata in
tutte le direzioni resta (a meno delle piccole perdite ohmiche nel metallo)
uguale alla potenza che il trasmettitore le fornisce.

Quello che il guadagno fa davvero è **concentrare** quella stessa energia:
invece di spargerla uniformemente su tutta la sfera, la incanala in un cono
più stretto in una direzione preferita, lasciando meno energia (spesso quasi
nulla) altrove. È una legge di conservazione: se il diagramma si stringe da
un lato, deve allargarsi/ridursi dall'altro.

Il dipolo `meshcore-ita-dipolo` (2,13 dBi) irradia quasi uniformemente
intorno a sé, a "ciambella": va bene per un nodo che deve sentire tutte le
direzioni. Il nostro `fabrizio-yagi-10el` (12,45 dBi) ha circa 10,3 dB di
guadagno in più rispetto al dipolo — un fattore di intensità di circa **10,7
volte** in linea retta nella direzione preferita (`10^(10,3/10) ≈ 10,7`) — ma
un raggio conico di irradiazione ampio solo **~40°** (vedi
[Diagramma di irradiazione](#diagramma)) invece dei quasi 360° del dipolo.

**In pratica:** più guadagno serve per collegamenti fissi punto-punto, dove
sai già in che direzione punta l'altro nodo e vuoi concentrare lì tutta
l'energia disponibile. Meno guadagno (dipolo, ground plane) serve per un nodo
che deve parlare con vicini sparsi in tutte le direzioni.

## Rapporto avanti/dietro {#avanti-dietro}

Il **rapporto avanti/dietro** (F/B, "front-to-back") è la differenza in dB
tra il guadagno nella direzione di massima irradiazione e il guadagno nella
direzione opposta (180° dietro). Misura quanto un'antenna direttiva
"ignora" segnali/interferenze che arrivano da dietro.

| Antenna | F/B | Fattore lineare (dietro è più debole di...) |
|---|---|---|
| Yagi 2 el. riflettore (Fabrizio) | 8,45 dB | ~7,0 volte |
| Yagi 2 el. direttore (Fabrizio) | 8,13 dB | ~6,5 volte |
| Yagi 3 elementi di riferimento | 5,93 dB | ~3,9 volte |
| Yagi 10 elementi (Fabrizio) | 22,8 dB | ~190 volte |

Un F/B modesto come 6–8 dB già aiuta parecchio contro un disturbo alle
spalle. Un F/B come i 22,8 dB della Yagi a 10 elementi è un'altra categoria:
quasi tutta l'energia che arriva da dietro (o va verso dietro in
trasmissione) viene scartata, utile quando dietro l'antenna c'è una fonte di
rumore radio o un altro collegamento da non disturbare.

## Come leggere un diagramma di irradiazione {#diagramma}

Il **diagramma di irradiazione** mostra quanto un'antenna irradia (o riceve)
in funzione della direzione. Ogni scheda di questa galleria mostra due
"tagli" (sezioni) del diagramma tridimensionale, più la vista 3D interattiva:

- **taglio in azimut**: guadagno intorno all'orizzonte (a 360°), a
  elevazione fissa — utile per capire in che direzioni orizzontali punta
  l'antenna.
- **taglio in elevazione**: guadagno dal basso verso l'alto lungo un piano
  verticale — utile per capire quanto l'antenna "spara" verso l'alto/basso
  invece che verso l'orizzonte (dove di solito serve, per collegamenti tra
  nodi alla stessa quota).

Vocabolario per leggerli:

- **lobo**: un "petalo" del diagramma, una zona angolare dove il guadagno è
  alto. Il **lobo principale** è quello di massimo guadagno (la direzione
  in cui punta l'antenna); i **lobi secondari** sono petali più piccoli in
  altre direzioni (energia "sprecata" fuori dalla direzione voluta).
- **nullo**: una direzione dove il guadagno crolla, spesso di decine di dB
  (in questa galleria il pavimento del grafico è tarato a −40 dBi). Un nodo
  esattamente in un nullo può risultare "invisibile" anche a distanza
  ravvicinata.
- **apertura a −3 dB (beamwidth)**: l'ampiezza angolare, intorno al lobo
  principale, entro cui il guadagno resta entro 3 dB dal massimo (cioè non
  scende sotto metà potenza). Dà un'idea pratica di quanto puoi sbagliare la
  mira dell'antenna prima di perdere metà segnale.

Esempi calcolati su antenne di questa galleria: la Yagi a 3 elementi di
riferimento e la Yagi 2 elementi con riflettore hanno un'apertura in azimut a
−3 dB di circa **70°** — abbastanza tollerante nel puntamento. La Yagi a 10
elementi, molto più direttiva, ha un cono a −3 dB di appena **~40°** di
apertura totale attorno all'asse del boom: va puntata con più cura, ma
premia chi lo fa con molto più guadagno e F/B.

## Impedenza: R + jX {#impedenza}

L'**impedenza** al punto di alimentazione di un'antenna è un numero
complesso, Z = R + jX:

- **R** (resistenza, parte reale): è dove va davvero l'energia — irradiata
  nello spazio (più una piccola quota persa in calore nei conduttori). È
  l'unica parte "utile".
- **X** (reattanza, parte immaginaria): energia che va e torna indietro ogni
  ciclo senza mai lasciare l'antenna, come una molla. X positiva si dice
  **induttiva**, X negativa **capacitiva**. Non irradia: se è grande, la
  maggior parte della potenza che il cavo cerca di consegnare rimbalza
  indietro verso il trasmettitore (quanto, esattamente, lo spiega il
  [ROS](#ros) subito dopo).

L'obiettivo, per collegare l'antenna a un cavo coassiale da 50 Ω senza
sprechi, è avere Z il più vicino possibile a 50 + j0 Ω.

| Antenna | Z simulata a 869,618 MHz |
|---|---|
| Dipolo di riferimento | 71,9 − j0,1 Ω |
| Ground plane di riferimento | 49,5 − j0,2 Ω |
| Yagi 3 elementi di riferimento | 40,7 − j0,3 Ω |
| Yagi 2 el. riflettore (Fabrizio) | 54,4 + j1,7 Ω |
| Yagi 2 el. direttore (Fabrizio) | 50,3 − j1,0 Ω |
| Yagi 10 elementi (Fabrizio) | 35,4 + j23,6 Ω |

Da dove viene la reattanza? Due cause tipiche:

1. **Lunghezza non perfettamente risonante** (vedi
   [Lunghezza d'onda](#lunghezza-onda)): un filo un po' più lungo del punto
   di risonanza dà X positiva (induttiva), un po' più corto dà X negativa
   (capacitiva).
2. **Accoppiamento con elementi parassiti vicini** (riflettore/direttore in
   una Yagi): la loro presenza induce corrente anche nell'elemento
   alimentato, e questo sposta la sua impedenza rispetto a quella che
   avrebbe da solo. È per questo che l'elemento alimentato di una Yagi va
   quasi sempre **accorciato rispetto alla sua lunghezza di risonanza da
   isolato**: l'accorciamento introduce apposta una piccola X capacitiva che
   cancella l'X induttiva portata dall'accoppiamento con i parassiti, così
   il risultato netto torna vicino a X = 0. È il motivo per cui, nella Yagi
   a 3 elementi di riferimento di questa galleria, il direttore (148,2 mm)
   è più lungo dell'elemento alimentato (145,0 mm): non è un errore, è
   l'elemento alimentato ad essere stato accorciato apposta per l'accoppiamento,
   non il direttore ad essere anomalo.

Il caso più estremo in questa galleria è la Yagi a 10 elementi:
**35,4 + j23,6 Ω**, con una X grande che da sola peggiora parecchio il ROS
(vedi sotto). Si vede anche stringendo le spaziature della Yagi a 3
elementi (esperimento descritto nella sua scheda): la resistenza R crolla e
la reattanza cresce, serve un adattamento più aggressivo (vedi
[Adattamento](#adattamento)).

## ROS, perdita di ritorno e potenza riflessa {#ros}

Il **ROS** (rapporto di onde stazionarie, in inglese SWR) è il modo pratico
di misurare quanto bene un'antenna è adattata al cavo (di solito 50 Ω), senza
dover leggere R e X separatamente. Si calcola dal **coefficiente di
riflessione** Γ:

```
Γ = (Z − Z₀) / (Z + Z₀)        ROS = (1 + |Γ|) / (1 − |Γ|)
```

con Z₀ = 50 Ω (l'impedenza di riferimento del cavo). ROS = 1,0 vuol dire
adattamento perfetto (Z = 50 + j0 Ω esatti, niente riflesso); più ROS sale,
più energia torna indietro invece di essere irradiata. La stessa Γ dà anche
la **perdita di ritorno** (return loss, quanto più è alta meglio è) e la
frazione di potenza riflessa |Γ|²:

| ROS | Γ | Perdita di ritorno | Potenza riflessa |
|---|---|---|---|
| 1,0 | 0 | ∞ | 0% |
| 1,2 | 0,091 | 20,8 dB | 0,8% |
| 1,5 | 0,200 | 14,0 dB | 4,0% |
| 2,0 | 0,333 | 9,5 dB | 11,1% |
| 3,0 | 0,500 | 6,0 dB | 25,0% |

**In pratica:**

- **ROS ≤ 1,5** (sotto il 4% riflesso): ottimo, va bene per qualsiasi
  trasmettitore.
- **ROS fino a 2** (11% riflesso): accettabile, la maggior parte dei
  moduli radio LoRa/MeshCore lo tollera senza problemi.
- **ROS 3 o oltre** (25% riflesso o più): un quarto (o più) della potenza
  torna indietro. Molti trasmettitori riducono automaticamente la potenza in
  uscita per proteggersi, o nel tempo si stressano; da evitare, serve un
  adattamento (vedi sotto).

Le antenne di questa galleria vanno da ROS 1,01 (ground plane di
riferimento) a ROS 1,91 (Yagi a 10 elementi, per via della X = +23,6 Ω non
compensata) — tutte comunque sotto la soglia critica di ROS 3.

## Adattamento: portare l'antenna a 50 Ω {#adattamento}

**Adattare** un'antenna vuol dire interporre, tra cavo e antenna, qualcosa
che trasformi l'impedenza reale dell'antenna in qualcosa di vicino a 50 + j0
Ω, per minimizzare il ROS. Tecniche comuni:

- **Balun** ("balanced-unbalanced"): un dipolo è un elemento **bilanciato**
  (le due metà sono simmetriche), ma il coassiale è **sbilanciato** (la
  calza è collegata a massa). Senza un balun, un po' di corrente scorre
  sulla calza esterna del cavo invece che solo sull'antenna: questo distorce
  il diagramma di irradiazione e falsa la lettura del ROS. Un balun semplice
  ("ugly balun") si fa avvolgendo qualche spira dello stesso cavo coassiale
  su sé stesso vicino al punto di alimentazione.
- **Choke** (impedenza di modo comune): stessa funzione del balun, spesso
  realizzata con perline di ferrite infilate sul cavo vicino al punto di
  alimentazione, per bloccare la corrente indesiderata sulla calza.
- **Adattamento a gamma** ("gamma match"): usato sulle Yagi quando
  l'elemento alimentato è una singola asta continua (non un dipolo spezzato
  al centro). Un'astina corta parallela a metà dell'elemento, collegata a
  un capo all'elemento e alimentata all'altro capo tramite un condensatore
  in serie, alza la R effettiva vista dal cavo e cancella parte della X.
  Utile quando la R dell'elemento alimentato è molto bassa, come
  nell'esperimento a spaziature strette della Yagi a 3 elementi di
  riferimento (R crolla a poche decine di Ω).
- **Adattamento a hairpin**: uno spezzone corto di linea cortocircuitato a
  "U" ai capi del punto di alimentazione. Se l'elemento alimentato è stato
  accorciato sotto risonanza (X negativa, capacitiva) l'induttanza
  dell'hairpin la cancella, alzando anche un po' la R. È il motivo per cui
  molte Yagi commerciali hanno l'elemento alimentato come un'unica asta
  dritta con un piccolo anello vicino al centro invece di un dipolo
  spezzato.
- **Trasformatore a λ/4**: uno spezzone di linea di trasmissione lungo un
  quarto d'onda (elettrico, cioè diviso per la velocità di propagazione di
  *quella* linea — non il λ/4 in aria di 86,19 mm calcolato sopra) e con
  impedenza caratteristica Zt = √(Z₀ · Zcarico) trasforma un'impedenza reale
  Zcarico nell'impedenza di linea Z₀ desiderata. Esempio: per portare
  un'ipotetica antenna da 36 Ω a 50 Ω, Zt = √(50 × 36) ≈ **42,4 Ω**.
- Per cancellare una reattanza pura (senza toccare R), un condensatore o
  un'induttanza in serie bastano da soli. Esempio numerico dalla Yagi a 10
  elementi di questa galleria (X = +23,6 Ω, induttiva): un condensatore in
  serie da circa **7,8 pF** a 869,618 MHz la cancellerebbe quasi del tutto
  (C = 1/(2π·f·X)), lasciando solo il disadattamento di R (35,4 Ω verso 50
  Ω, un ROS più ragionevole) da sistemare con un trasformatore o una rete a
  L.

Perché **50 Ω** e non un altro valore: è un compromesso storico tra
l'impedenza di cavo coassiale che minimizza le perdite nel dielettrico
(vicina a 77 Ω) e quella che massimizza la potenza gestibile prima di
scaricare elettricamente il dielettrico (vicina a 30 Ω). 50 Ω è nel mezzo, ed
è diventato lo standard universale: ogni modulo radio LoRa/MeshCore, ogni
connettore SMA o N di questa galleria, è progettato per 50 Ω. È per questo
che ogni scheda di questa galleria riporta il ROS calcolato proprio su una
linea da 50 Ω.

## ERP: il limite di potenza del preset italiano {#erp}

Il preset italiano di MeshCore usa la sotto-banda **869,4–869,65 MHz**, dove
il regolamento consente al massimo **500 mW ERP** (equivalent radiated
power, potenza equivalente irradiata **rispetto a un dipolo a mezz'onda**,
quindi in **dBd**, non dBi — vedi [dBi e dBd](#dbi-dbd)) e un **duty cycle**
del 10%. In decibel, 500 mW ERP corrisponde a `10·log₁₀(500) ≈ 27 dBm ERP`.
Il testo normativo completo è sulla pagina
[normativa](https://meshcore-ita.github.io/normativa/) del progetto.

La formula per calcolare l'ERP effettivo del tuo impianto è:

```
ERP (dBm) = Ptx (dBm) − perdita cavo (dB) + guadagno antenna (dBd)
```

dove Ptx è la potenza che il trasmettitore mette in uscita (prima del cavo),
la perdita cavo è quella del coassiale tra radio e antenna alla frequenza di
lavoro (i produttori di cavo la danno in dB/metro), e il guadagno va
convertito in dBd se lo hai in dBi (sottrai 2,15).

Esempi calcolati:

| Ptx | Perdita cavo | Guadagno antenna | ERP calcolato | Limite 27 dBm / 500 mW |
|---|---|---|---|---|
| 100 mW (20 dBm) | 0,5 dB | 6,36 dBi (4,21 dBd, riflettore) | 23,71 dBm ≈ 235 mW | rispettato |
| 500 mW (27,0 dBm) | 1,0 dB | 2,15 dBi (0 dBd, dipolo) | 25,99 dBm ≈ 397 mW | rispettato |
| 100 mW (20 dBm) | 1,5 dB | 8,05 dBi (5,90 dBd, Yagi 3 el.) | 24,40 dBm ≈ 275 mW | rispettato |
| 1000 mW (30 dBm) | 2,0 dB | 2,15 dBi (0 dBd, dipolo) | 28,00 dBm ≈ 631 mW | **supera il limite** |

L'ultimo esempio mostra un caso comune di errore: alzare la potenza del
trasmettitore a 1 W pensando "tanto il guadagno dell'antenna è basso" può
comunque sforare il limite se il cavo è corto/buono. Prima di alzare Ptx,
ricalcola l'ERP con la formula sopra.

Puoi anche ribaltare la formula per sapere quanta potenza puoi mettere in
antenna restando a 27 dBm ERP:

```
Ptx max (dBm) = 27 − guadagno (dBd) + perdita cavo (dB)
```

Esempio: con 0,5 dB di perdita cavo e i 6,36 dBi (4,21 dBd) della Yagi
riflettore, Ptx max ≈ **23,3 dBm ≈ 213 mW**. Con il dipolo di riferimento
(0 dBd) e 1 dB di cavo, invece, Ptx max ≈ **28,0 dBm ≈ 631 mW** — ma resta
comunque il limite dei 27 dBm/500 mW **ERP**, quindi in pratica ci si ferma
lì con Ptx a monte del cavo.

Il **duty cycle 10%** limita indipendentemente il tempo di trasmissione: al
massimo il 10% di una qualunque finestra temporale, cioè ad esempio non più
di 6 minuti ogni ora (`0,10 × 60 min = 6 min`). MeshCore, gestendo da solo
contese e ritrasmissioni sulla mesh, in condizioni normali resta ben sotto
questa soglia; diventa rilevante solo con traffico anomalo o test
manuali ravvicinati.

Per capire come l'ERP si traduce in portata reale (insieme a sensibilità del
ricevitore, margine di collegamento, ostacoli), vedi la pagina
[link budget](https://meshcore-ita.github.io/link-budget/).

## Le schede NEC usate in questa galleria {#schede-nec}

I file `antenna.nec` sono testo semplice: una riga, una "scheda" (card) di
due lettere maiuscole seguita da campi numerici (separati da spazi o
virgole). Il parser di questa galleria (`tools/nec.py`) supporta queste:

| Scheda | Significato | Campi principali |
|---|---|---|
| `CM` | Commento (una riga di descrizione, può ripetersi) | testo libero |
| `CE` | Fine dei commenti, inizia la geometria | (nessuno) |
| `SY` | Definisce una variabile (come in 4nec2), utilizzabile nelle righe dopo | `nome=espressione` |
| `GW` | Un filo (wire): tag, segmenti, coordinate estremi, raggio | tag, n° segmenti, x1 y1 z1, x2 y2 z2, raggio (tutto in metri) |
| `GE` | Fine geometria; il numero indica se c'è un piano di terra | 0 = nessun piano immagine, 1 = con piano immagine |
| `EK` | Attiva il "thin-wire kernel esteso", più accurato per fili spessi rispetto alla lunghezza dei segmenti | (nessun campo, o `-1` per disattivarlo) |
| `GN` | Tipo di terreno sotto l'antenna | tipo (−1 spazio libero, 0 terreno reale, 1 terreno perfetto), n° radiali, poi costante dielettrica e conducibilità |
| `EX` | Sorgente di eccitazione (dove si alimenta) | tipo (0 = generatore di tensione), tag del filo, numero di segmento |
| `LD` | Carico/perdita su uno o più segmenti (es. conducibilità reale di un metallo) | tipo, tag (0 = tutti), segmento iniziale, segmento finale, valore |
| `FR` | Frequenza di lavoro | ..., frequenza in MHz |
| `RP` | Richiesta di diagramma di irradiazione | **ignorata da questa galleria**: il diagramma lo ricalcola sempre lei stessa, per uniformità tra tutte le schede |
| `EN` | Fine del file | (nessun campo; tutto dopo viene ignorato) |

Nota: `RP`, `PT` ed `EN` sono lette per compatibilità con 4nec2/xnec2c/EZNEC
(così lo stesso file si apre anche lì), ma solo `EN` ha effetto nel parser di
questa galleria: dice dove fermarsi.

**Regola pratica sui segmenti** (quante volte dividere ogni `GW`): due
condizioni, entrambe da rispettare per una simulazione affidabile con il
modello NEC-2 a filo sottile:

1. **almeno 10 segmenti per ogni mezza lunghezza d'onda** di filo (più
   segmenti = più precisione, ma anche più tempo di calcolo);
2. **lunghezza di ciascun segmento > 4 volte il raggio del filo**, perché
   sotto questa soglia l'approssimazione "filo sottile" di NEC-2 perde
   accuratezza (per questo i modelli di questa galleria usano anche `EK`,
   che allarga un po' il margine per fili relativamente spessi).

Esempio verificato sul modello della Yagi a 3 elementi di riferimento:
l'elemento riflettore è lungo 172,4 mm su 21 segmenti, cioè 8,2 mm a
segmento; il raggio del filo è 2 mm, quindi il rapporto è `8,2 / 2 = 4,1`:
appena sopra la soglia minima di 4. Il dipolo di riferimento (160,6 mm su 21
segmenti, raggio 1 mm) sta molto più comodo, con rapporto 7,65.

## Dal modello alla realtà {#dal-modello-alla-realta}

Una simulazione NEC-2 in spazio libero è un punto di partenza, non l'ultima
parola. Cose che cambiano quando l'antenna diventa un oggetto vero, montato
da qualche parte:

- **Diametro del filo/tubo**: se costruisci con un diametro diverso da
  quello del modello, la lunghezza di risonanza cambia (vedi
  [Lunghezza d'onda](#lunghezza-onda) — più il conduttore è spesso, più va
  accorciato). Se cambi materiale/diametro rispetto al file scaricato,
  riparti dalla lunghezza teorica e ritara.
- **Supporti in materiale plastico** (boom in PVC, morsetti stampati in
  3D/resina, come nelle Yagi di Fabrizio di questa galleria): sono quasi
  trasparenti alle radiofrequenze, in genere non serve compensarli.
- **Supporti o boom metallici**: un boom o un'asta metallica vicino agli
  elementi si comporta come un ulteriore elemento parassita non voluto, e
  detiene sia l'impedenza sia il diagramma. Il file della Yagi a 10 elementi
  di questa galleria documenta esattamente questo caso: i commenti originali
  (in tedesco) prevedono correzioni di +6 mm sugli elementi e +12 mm
  sull'alimentato per compensare un boom metallico — un esempio reale di
  quanto possa contare.
- **Un'asta o un palo metallico vicino** (come il tondino filettato
  verticale sotto il boom della Yagi con riflettore installata sul nodo
  pybot): può accoppiarsi con gli elementi allo stesso modo. Tienilo il più
  lontano possibile dagli elementi, o verifica con una misura che
  l'adattamento non sia peggiorato rispetto al modello.
- **Percorso del cavo coassiale e corrente di modo comune**: un tratto di
  coassiale che corre parallelo e vicino agli elementi (come nella Yagi con
  riflettore, dove il cavo passa vicino agli elementi) può irradiare a sua
  volta e alterare il diagramma misurato rispetto a quello simulato. Fai
  uscire il cavo perpendicolare agli elementi per un tratto, e usa un
  balun/choke (vedi [Adattamento](#adattamento)).
- **Terreno, tetto, oggetti vicini**: le simulazioni di questa galleria sono
  in spazio libero (tranne dove il file include esplicitamente un piano di
  terra). Un'antenna vera montata su un tetto, vicino a grondaie, altre
  antenne o pannelli solari, si comporta diversamente: aspettati di dover
  ritarare leggermente.
- **Misura con un NanoVNA**: dopo aver costruito l'antenna, collega il
  NanoVNA il più vicino possibile al punto di alimentazione (uno spezzone
  corto di cavo, non 10 metri di coassiale) e leggi Z e ROS a 869,618 MHz.
  Se il minimo ROS (la risonanza) cade a una frequenza diversa da quella
  attesa, accorcia per spostarlo più in alto, allunga per spostarlo più in
  basso, ripetendo a piccoli passi. Anche solo un misuratore di ROS in
  linea, senza il dettaglio di R e X, è già utile per verificare
  l'adattamento prima di trasmettere.
