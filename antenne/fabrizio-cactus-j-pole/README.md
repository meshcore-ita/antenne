# Cactus J-Pole: una J-pole disaccoppiata dal palo

La **Cactus J-Pole** è una variante della J-pole progettata per essere montata direttamente su un palo conduttivo. Alla struttura tradizionale aggiunge uno **stub di disaccoppiamento del palo** (*mast decoupling stub*), che limita le correnti RF dirette verso il supporto.

In una J-pole classica il palo metallico e la parte esterna del cavo coassiale possono partecipare alla radiazione. Il risultato può dipendere dalla lunghezza del palo, dalla posizione di montaggio e dal percorso del cavo. Per questo spesso si installa la J-pole su un supporto isolante e si presta attenzione alle correnti di modo comune.

## Come funziona

La parte superiore mantiene il principio della J-pole: un radiatore verticale di circa mezza lunghezza d'onda, alimentato attraverso una sezione di adattamento di circa un quarto d'onda. Sotto questa sezione si aggiunge un secondo stub conduttivo, ripiegato verso l'alto e disposto vicino al palo.

Alla frequenza di progetto, lo stub produce un punto ad **alta impedenza RF** fra l'antenna e il palo. Riducendo la corrente che prosegue nel supporto, permette di usare un palo metallico anche lungo senza che la sua lunghezza diventi un elemento determinante per il funzionamento dell'antenna. Il disaccoppiamento non è idealmente infinito nella realizzazione pratica: dimensioni, giunzioni e installazione vanno comunque verificate.

Lo stub è lungo *approssimativamente* un quarto d'onda. Il progetto originale indica come riferimento la **lunghezza elettrica complessiva** fra l'estremità dello stub e il punto immediatamente sotto la J-pole tradizionale, pari a circa mezza lunghezza d'onda. Queste proporzioni sono un punto di partenza per la simulazione e la taratura, non quote di taglio universali.

## Variare il palo nel modello NEC2

Nel modello NEC2 fornito, la variabile `pole` rappresenta la **lunghezza del palo metallico sotto lo stub di disaccoppiamento**, espressa in metri. Il valore iniziale è `0.1`, cioè 10 cm. È usata per determinare l'estremità inferiore dell'elemento `GW 10`:

```nec
SY pole=0.1
GW 10 5 0 0 height-_lambda/4 0 0 height-_lambda/4-pole wire
```

Variando `pole` e ripetendo la simulazione, **l'antenna si comporta sostanzialmente allo stesso modo nel modello**: la lunghezza del palo non determina più la risposta della parte radiante come può accadere con una J-pole classica montata direttamente su un supporto conduttivo. È questo l'effetto che si vuole ottenere con il *mast decoupling stub*.

Il file usa `GN -1`, quindi simula la struttura **in spazio libero**. Il risultato riguarda quella geometria, quella frequenza e il punto di alimentazione rappresentati nel modello; per verificare una costruzione reale occorre misurare anche l'effetto del cavo e del montaggio.

## Alimentazione e costruzione

Il progetto descritto da John S. Huggins propone anche due accorgimenti distinti dallo stub:

- **Connessione di alimentazione a bassa induttanza:** conduttori più larghi e un collegamento corto fra linea e sezione di adattamento.
- **Linea di alimentazione interna:** il coassiale può passare dentro i tubi; in alternativa, il tubo stesso può fungere da conduttore esterno di una linea coassiale interna. Il connettore può così essere collocato più in basso, sul fondo o lateralmente al palo.

L'alimentazione interna richiede particolare cura nel collegamento continuo della schermatura al tubo. La possibilità di fare a meno di un choke esterno è presentata nell'articolo come risultato delle simulazioni e come obiettivo costruttivo: va verificata sul prototipo, misurando anche le correnti di modo comune. Lo stub di disaccoppiamento del palo resta utile anche scegliendo un'alimentazione esterna.

## Verifiche sul prototipo

Prima dell'installazione definitiva conviene misurare l'impedenza o il ROS alla frequenza di utilizzo, controllare la risposta con il palo e il cavo nella configurazione reale e confrontare, se possibile, la corrente RF sul palo con e senza stub. Le dimensioni fisiche dipendono dalla frequenza, dal diametro dei conduttori, dalle spaziature e dai dettagli dei collegamenti.

## Brevetto e pubblicazione del prototipo

La configurazione *mast mountable antenna* descritta da John S. Huggins è oggetto del brevetto statunitense [US10468743B2](https://patents.google.com/patent/US10468743B2/en), concesso nel 2019. Questo repository documenta un prototipo sperimentale e il relativo modello NEC2: la pubblicazione di descrizioni, fotografie proprie, misure e simulazioni non conferisce una licenza per lo sfruttamento dell'invenzione brevettata.

I brevetti hanno efficacia territoriale. La scheda del brevetto consultata riporta gli Stati Uniti nella sezione «Country Status»; prima di produrre, distribuire o vendere antenne basate sul progetto occorre verificare i diritti effettivamente in vigore nei paesi interessati e le specifiche rivendicazioni. Per gli atti privati non commerciali e gli esperimenti relativi all'invenzione possono applicarsi eccezioni previste dalla normativa pertinente.

Fotografie, disegni e testi dell'articolo originale possono avere una tutela distinta dal brevetto: per documentare il prototipo si usano contenuti propri e si cita la fonte. Un'eventuale licenza del file NEC2 riguarda quel file e non costituisce una licenza sul brevetto.

## Riferimento

- John S. Huggins, [*Mast Mountable J-Pole Antenna*](https://www.hamradio.me/antennas/mast-mountable-j-pole-antenna.html). Descrizione della geometria, dello stub di disaccoppiamento, delle opzioni di alimentazione e delle simulazioni del progetto.
- John S. Huggins, [US10468743B2 — *Mast mountable antenna*](https://patents.google.com/patent/US10468743B2/en), brevetto statunitense.
- lex_ph2lb, [*Antenna experiment - 868MHz J-pole*](https://www.thethingsnetwork.org/forum/t/antenna-experiment-868mhz-j-pole/3620?utm_source=chatgpt.com). Analisi e modello nec 868 Mhz J-Pole
