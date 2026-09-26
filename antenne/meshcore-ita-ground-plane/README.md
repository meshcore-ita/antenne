## Come funziona

Una **ground plane** è, elettricamente, metà di un [dipolo](../guida/#dipolo):
uno stilo verticale lungo circa λ/4 al posto di uno dei due bracci, e al
posto dell'altro braccio un gruppo di **radiali** (fili o tondini che
partono dallo stesso punto e vanno verso il basso/lateralmente) che fanno
da riferimento di massa artificiale, al posto di un piano di terra reale che
in cima a un palo non esiste.

L'angolo dei radiali non è un dettaglio estetico: è la manopola principale
per regolare l'[impedenza](../guida/#impedenza) al punto di alimentazione.
Con 4 radiali **inclinati a 45°** verso il basso, come in questo modello,
l'impedenza simulata cade quasi esattamente su 50 Ω, senza bisogno di
nessun adattamento aggiuntivo — motivo per cui questa è la geometria scelta
come riferimento.

## Misure

| Elemento | Lunghezza | Diametro | Note |
|---|---|---|---|
| Stilo verticale | 77,5 mm | 2 mm (rame) | ≈ λ/4 accorciato del 10,1% rispetto al teorico (86,19 mm, vedi [Lunghezza d'onda](../guida/#lunghezza-onda)) |
| Radiali (× 4) | 81,375 mm (1,05 × stilo) | 2 mm (rame) | Inclinati a 45° sotto il piano orizzontale, a 90° uno dall'altro |

Simulazione NEC-2 a 869,618 MHz, spazio libero, polarizzazione verticale:

| Grandezza | Valore |
|---|---|
| [Impedenza](../guida/#impedenza) | 49,5 − j0,2 Ω |
| [ROS](../guida/#ros) su 50 Ω | 1,01 |
| Guadagno | 2,2 dBi (~0,1 dBd) |

## Materiali

- Tondino/filo di rame da 2 mm: uno spezzone per lo stilo, quattro per i
  radiali.
- Connettore da pannello SMA o N femmina, montato su una piccola piastra o
  scatola stagna che faccia anche da punto di ancoraggio meccanico per i 4
  radiali.
- Un supporto isolante (plastica) per tenere lo stilo in asse sopra il
  connettore, se il connettore da solo non basta a sostenerlo rigidamente.

## Costruzione passo per passo

**Lista di taglio:** 1 stilo da **77,5 mm** + 4 radiali da **81,4 mm**,
tutti in tondino di rame da 2 mm (scorta di qualche decimo di mm su ogni
pezzo per la rifinitura finale).

1. Salda o avvita lo stilo (77,5 mm) al piedino centrale del connettore,
   verticale, in asse con il connettore.
2. Fissa i 4 radiali (81,4 mm) al corpo/flangia di massa del connettore,
   distribuiti a 90° l'uno dall'altro, inclinati a **45° verso il basso**
   rispetto al piano orizzontale (non dritti in orizzontale: vedi
   l'esperimento sotto per capire perché conta).
3. Verifica che stilo e radiali siano tutti alla stessa altezza di partenza
   (lo stesso punto elettrico, il connettore) e che lo stilo resti verticale
   una volta montato (vedi [Polarizzazione](../guida/#polarizzazione)).
4. Se il connettore da solo non regge meccanicamente lo stilo, aggiungi un
   piccolo supporto isolante (plastica) alla base per irrigidirlo.
5. Misura con un NanoVNA il più vicino possibile al connettore: se il
   minimo ROS non cade vicino a 869,618 MHz, accorcia lo stilo (non i
   radiali) di un paio di decimi di millimetro alla volta.
6. Impermeabilizza le saldature con nastro autovulcanizzante o resina prima
   di installarla all'esterno.

## Esperimenti da provare

**Radiali orizzontali invece che a 45°.** È l'esperimento più istruttivo su
questa antenna. Si legge spesso che una ground plane con 4 radiali
perfettamente orizzontali abbia un'impedenza intorno a 36 Ω — il
ragionamento di solito citato è che un piano di terra infinito dimezza
esattamente l'impedenza di un dipolo (73 / 2 ≈ 36,5 Ω, per teoria delle
immagini). Abbiamo verificato questo numero **rifacendo la simulazione**
invece di fidarci a memoria, ritarando la lunghezza dello stilo per tornare
in risonanza con i radiali orizzontali (mantenendo lo stesso rapporto
radiali/stilo di 1,05): il risultato è una resistenza intorno a **~25 Ω**,
non 36 Ω.

La differenza ha una spiegazione precisa: i 36,5 Ω "da manuale" valgono per
un piano di terra **infinito e continuo**, cioè l'immagine perfetta di un
dipolo. Quattro radiali discreti, per quanto orizzontali, non sono un piano
infinito: si comportano da riferimento di massa più "debole", e la
resistenza al punto di alimentazione scende sotto quel valore teorico.
Inclinare i radiali verso il basso (drooping) è esattamente la tecnica che
i costruttori usano da decenni per **risalire** verso 50 Ω partendo da
quella resistenza più bassa — coerente con i 49,5 Ω che questo stesso
modello, con i radiali a 45°, raggiunge già senza nessun adattamento
aggiuntivo.

**In pratica:** se costruisci questa antenna con radiali orizzontali invece
che a 45° e trovi un ROS più alto del previsto, non è un errore di
costruzione: è la geometria che lo spiega. Prova a piegare gradualmente i
radiali verso il basso e a rimisurare: dovresti vedere l'impedenza salire
avvicinandosi ai 50 Ω via via che l'angolo si avvicina ai 45°.

Altri esperimenti:

- Prova con 3 o 6 radiali invece di 4 (a parità di angolo e lunghezza) e
  osserva se il ROS cambia: più radiali si avvicinano di più al "piano
  infinito" ideale.
- Confronta questa antenna con il
  [dipolo di riferimento](../meshcore-ita-dipolo/): stessa idea di base (un
  quarto d'onda alimentato), ma il secondo "braccio" è sostituito dai
  radiali. Nota come l'impedenza scenda da 71,9 Ω (dipolo) a 49,5 Ω (ground
  plane con radiali a 45°).

## Errori comuni

- **Montare i radiali orizzontali aspettandosi 50 Ω**: come spiegato sopra,
  con soli 4 radiali orizzontali l'impedenza reale è più vicina a 25 Ω che
  a 36 Ω o 50 Ω.
- **Accorciare i radiali invece dello stilo per ritarare**: sono i radiali
  a fissare soprattutto l'impedenza, mentre è la lunghezza dello **stilo**
  a spostare la frequenza di risonanza; se il NanoVNA mostra la risonanza
  fuori posto, agisci sullo stilo.
- **Dimenticare il piano isolante alla base**: senza un buon isolamento
  meccanico tra stilo e struttura di supporto metallica, quest'ultima può
  accoppiarsi elettricamente e alterare sia impedenza sia diagramma.

## Note

Antenna omnidirezionale: utile come riferimento per confrontare la
copertura reale di antenne direttive (le Yagi di questa galleria) rispetto
a un'antenna che non concentra energia in nessuna direzione particolare
(vedi [Guadagno](../guida/#guadagno)).
