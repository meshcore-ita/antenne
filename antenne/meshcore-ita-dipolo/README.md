## Come funziona

Questo è il [dipolo](../guida/#dipolo) a mezz'onda più semplice possibile:
un filo di rame da 2 mm di diametro, dritto, alimentato esattamente al
centro. Non ha guadagno da vendere (è il riferimento "0 dBd" descritto in
[dBi e dBd](../guida/#dbi-dbd)), ma è il modello più utile per capire tutti
i concetti di base prima di passare a Yagi più complesse: lunghezza
risonante, impedenza, ROS.

Serve anche come **antenna di riferimento vera e propria**: per un nodo che
deve sentire tutte le direzioni allo stesso modo (un nodo centrale, un
ripetitore), un dipolo semplice va benissimo e non richiede nessun
adattamento.

## Misure

| Grandezza | Valore |
|---|---|
| Lunghezza totale | 160,6 mm |
| Diametro filo | 2 mm (rame) |
| Lunghezza teorica λ/2 | 172,37 mm (vedi [Lunghezza d'onda](../guida/#lunghezza-onda)) |
| Accorciamento rispetto al teorico | 6,8% |

Simulazione NEC-2 a 869,618 MHz, spazio libero, polarizzazione verticale:

| Grandezza | Valore |
|---|---|
| [Impedenza](../guida/#impedenza) | 71,9 − j0,1 Ω |
| [ROS](../guida/#ros) su 50 Ω | 1,44 (circa 3,2% di potenza riflessa) |
| Guadagno | 2,1 dBi (~0 dBd, il riferimento stesso) |

## Materiali

- Filo o tondino di rame pieno, diametro 2 mm, lunghezza minima 165–170 mm
  (qualche mm di scorta per rifilare dopo la misura).
- Un connettore da pannello, SMA femmina o N femmina, con corpo/flangia a
  cui saldare o avvitare un braccio del dipolo, e piedino centrale per
  l'altro braccio.
- Qualche perlina di ferrite passante (choke) da infilare sul cavo
  coassiale vicino al connettore.
- Stagno, saldatore, sigillante/nastro autovulcanizzante per proteggere la
  saldatura dalle intemperie.

## Costruzione passo per passo

**Lista di taglio:** 2 bracci da **80,3 mm** ciascuno (metà di 160,6 mm),
in filo di rame da 2 mm.

1. Taglia i due bracci a 80,3 mm, lasciando qualche decimo di millimetro di
   scorta da rifilare dopo la misura con NanoVNA.
2. Prendi un connettore SMA (o N) femmina da pannello: il piedino centrale
   diventa il punto di saldatura del primo braccio, il corpo/flangia
   metallica (massa) quello del secondo.
3. Salda un braccio al piedino centrale del connettore e l'altro al corpo
   metallico, lasciando un piccolo distacco (1–2 mm) tra i due bracci
   esattamente sull'asse del connettore: è il "gap" di alimentazione del
   dipolo.
4. Allinea i due bracci in linea retta, verticali una volta installati
   (vedi [Polarizzazione](../guida/#polarizzazione)).
5. Avvita il connettore del dipolo direttamente sul cavo coassiale (o su un
   breve adattatore), e infila 4–6 perline di ferrite sul cavo, il più
   vicino possibile al connettore: è un **choke** (vedi
   [Adattamento](../guida/#adattamento)) che impedisce alla corrente di
   scorrere sulla calza esterna del cavo invece che solo sull'antenna.
6. Misura con un NanoVNA collegato il più vicino possibile al connettore:
   se il minimo ROS non cade vicino a 869,618 MHz, accorcia entrambi i
   bracci di un paio di decimi di millimetro alla volta (accorciare sposta
   la risonanza più in alto in frequenza).
7. Sigilla la saldatura e il gap con nastro autovulcanizzante o resina, per
   proteggerli dall'umidità.

## Esperimenti da provare

- Misura il ROS con e senza le perline di ferrite sul cavo: la differenza
  che vedi è dovuta proprio alla corrente di modo comune spiegata in
  [Adattamento](../guida/#adattamento) — con un cavo lungo e senza choke, il
  ROS misurato può apparire diverso (e meno ripetibile spostando il cavo)
  da quello simulato.
- Confronta questo dipolo con la
  [ground plane di riferimento](../meshcore-ita-ground-plane/): stesso
  principio di base (un quarto d'onda alimentato), ma con radiali al posto
  del secondo braccio. Nota come cambia l'impedenza (71,9 Ω contro 49,5 Ω).
- Prova ad allungare o accorciare il dipolo di 5 mm per volta (in
  simulazione o fisicamente) e osserva come si sposta la frequenza di
  risonanza: è l'esperimento più diretto per capire
  [Lunghezza d'onda](../guida/#lunghezza-onda) e [Impedenza](../guida/#impedenza)
  senza dover leggere formule.

## Errori comuni

- **Dimenticare il choke/balun**: un dipolo è un elemento bilanciato (vedi
  sotto, "Perché 72 Ω e come alimentarlo"), alimentato da un cavo
  sbilanciato. Senza un choke la corrente di modo comune sulla calza
  distorce il diagramma di irradiazione reale rispetto a quello simulato
  qui, che assume un'alimentazione perfettamente bilanciata.
- **Montarlo orizzontale**: rompe la polarizzazione verticale della rete
  MeshCore ITA (vedi [Polarizzazione](../guida/#polarizzazione)).
- **Aspettarsi ROS 1,0**: un dipolo semplice ha un'impedenza naturale
  vicina a 72 Ω, non 50 Ω (vedi sotto): un ROS intorno a 1,4–1,5 è normale e
  già ottimo, non un difetto di costruzione.

## Note

### Perché 72 Ω e come alimentarlo

Il dipolo a mezz'onda in filo sottile ha un'impedenza teorica di
riferimento di circa 73 Ω (qui simulata 71,9 Ω, molto vicina), non 50 Ω. È
una proprietà della sua geometria, non un difetto: il ROS di 1,44 che ne
risulta su un cavo da 50 Ω corrisponde ad appena il 3,2% di potenza
riflessa, ben dentro la soglia "ottima" descritta in
[ROS](../guida/#ros) (ROS ≤ 1,5). Per la maggior parte degli usi con
MeshCore **non serve nessun adattamento aggiuntivo**: si collega
direttamente al cavo da 50 Ω.

Se invece si vuole un ROS più vicino a 1,0, le due strade classiche sono:

- un **dipolo ripiegato** (folded dipole): usando due fili invece di uno,
  collegati alle estremità, l'impedenza al centro sale a circa 4 volte
  quella di un dipolo semplice (nell'ordine di 280–300 Ω), che va poi
  riportata a 50 Ω con un balun 4:1 o 6:1;
- una piccola rete a L o un trasformatore a λ/4 (vedi
  [Adattamento](../guida/#adattamento)), dimensionati per la Zt necessaria
  a trasformare ~72 Ω in 50 Ω.

In entrambi i casi, il dipolo resta un elemento **bilanciato**: che tu lo
alimenti diretto o tramite una di queste reti, serve sempre un balun o un
choke (perline di ferrite, come al passo 5 della costruzione) tra il cavo
coassiale sbilanciato e il punto di alimentazione, altrimenti parte della
corrente scorre sulla calza del cavo invece che solo sull'antenna,
alterando sia il diagramma sia la misura del ROS.
