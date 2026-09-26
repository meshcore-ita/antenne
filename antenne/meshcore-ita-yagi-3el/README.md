## Come funziona

Questa Yagi ha tutti e tre gli elementi che si trovano separati nelle due
Yagi a 2 elementi di Fabrizio di questa galleria: un
[dipolo](../guida/#dipolo) alimentato, con un **riflettore** dietro (come in
[fabrizio-yagi-2el-riflettore](../fabrizio-yagi-2el-riflettore/)) e un
**direttore** davanti (come in
[fabrizio-yagi-2el-direttore](../fabrizio-yagi-2el-direttore/)) insieme sullo
stesso boom. Il riflettore rimanda in avanti l'energia che andrebbe
irradiata all'indietro, il direttore concentra ulteriormente in avanti
quella che uscirebbe di lato: insieme danno più
[guadagno](../guida/#guadagno) e più
[rapporto avanti/dietro](../guida/#avanti-dietro) di ciascuno dei due da
solo, restando comunque un progetto semplice, alimentabile a 50 Ω senza reti
di adattamento.

Guardando le lunghezze sembra un controsenso: il direttore (148,2 mm) è più
**lungo** dell'elemento alimentato (145,0 mm), mentre nella scheda
["Impedenza"](../guida/#impedenza) della guida abbiamo spiegato che un
direttore deve essere più corto del dipolo risonante. Non è un errore: è
l'elemento **alimentato** a essere più corto del normale, non il direttore a
essere anomalo. Un dipolo isolato in un tubo da 4 mm risuonerebbe intorno ai
160 mm (vedi [Lunghezza d'onda](../guida/#lunghezza-onda)); qui è stato
accorciato apposta a 145,0 mm perché l'accoppiamento con riflettore e
direttore, entrambi vicini, induce sull'alimentato una reattanza induttiva
che va cancellata accorciandolo. Il risultato netto, verificato in
simulazione, è un'impedenza quasi puramente resistiva (40,7 − j0,3 Ω): la
reattanza indotta dai parassiti è compensata quasi esattamente
dall'accorciamento.

## Misure

| Elemento | Lunghezza | In λ | Distanza dal riflettore |
|---|---|---|---|
| Riflettore | 172,4 mm | 0,50 λ | 0 (origine del boom) |
| Alimentato (driven) | 145,0 mm | — (accorciato per l'accoppiamento) | 103,4 mm (0,30 λ) |
| Direttore | 148,2 mm | 0,43 λ | 189,6 mm (0,55 λ, cioè 86,2 mm / 0,25 λ dopo l'alimentato) |

Tubo/tondino da 4 mm di diametro per tutti e tre gli elementi. Boom totale
189,6 mm.

Simulazione NEC-2 a 869,618 MHz, spazio libero, polarizzazione verticale:

| Grandezza | Valore |
|---|---|
| [Impedenza](../guida/#impedenza) | 40,7 − j0,3 Ω |
| [ROS](../guida/#ros) su 50 Ω | 1,23 |
| [Guadagno](../guida/#guadagno) | 8,1 dBi (5,9 dBd, vedi [dBi/dBd](../guida/#dbi-dbd)) |
| [Avanti/dietro](../guida/#avanti-dietro) | 5,9 dB (~3,9× in lineare) |
| ROS minimo | a 874 MHz |
| Apertura azimutale a −3 dB | ≈ 70° (vedi [Diagramma](../guida/#diagramma)) |

Un ROS di 1,23 è comodamente sotto la soglia "ottima" di 1,5 (vedi
[ROS](../guida/#ros)): questa geometria si alimenta direttamente a 50 Ω,
senza gamma match, hairpin o trasformatori.

## Materiali

Tubo o tondino conduttore da 4 mm di diametro (rame o alluminio, la
simulazione non distingue il materiale se la conducibilità è alta e non
viene modellata una perdita esplicita). Boom non conduttivo (plastica,
legno trattato, vetroresina) per non introdurre l'effetto "boom metallico"
descritto nella scheda della [Yagi a 10 elementi](../fabrizio-yagi-10el/).

## Costruzione passo per passo

**Lista di taglio** (tubo/tondino da 4 mm):

- 1 riflettore: **172,4 mm**
- 1 alimentato: **145,0 mm**
- 1 direttore: **148,2 mm**

**Posizioni sul boom** (dall'estremità del riflettore):

- riflettore a 0 mm
- alimentato a **103,4 mm**
- direttore a **189,6 mm** (fine del boom)

Passi:

1. Taglia i tre elementi alle lunghezze sopra, con qualche decimo di
   millimetro di scorta da rifilare dopo la misura.
2. Segna sul boom le tre posizioni (0, 103,4 e 189,6 mm) e monta riflettore
   e direttore passanti, isolati elettricamente dal boom, centrati e
   **verticali** (vedi [Polarizzazione](../guida/#polarizzazione)).
3. Monta l'alimentato allo stesso modo, ma con un piccolo gap centrale (1–2
   mm) per il punto di alimentazione, come nel
   [dipolo di riferimento](../meshcore-ita-dipolo/).
4. Collega il cavo coassiale al gap dell'alimentato, con il cavo il più
   perpendicolare possibile agli elementi per un tratto prima di scendere
   verso il boom, e alcune perline di ferrite (choke) vicino al punto di
   alimentazione (vedi [Adattamento](../guida/#adattamento)).
5. Misura con un NanoVNA il più vicino possibile al punto di alimentazione:
   se il minimo ROS non cade vicino a 869,618 MHz, ritara leggermente la
   lunghezza dell'alimentato (non gli elementi parassiti).

## Esperimenti da provare

**Spaziature strette: il compromesso guadagno / avanti-dietro / impedenza.**
Le spaziature scelte qui (0,30 λ tra riflettore e alimentato, 0,25 λ tra
alimentato e direttore) non sono casuali: sono un compromesso pensato per
restare alimentabile direttamente a 50 Ω. Restringendo le spaziature a 0,20 λ
e 0,15 λ, mantenendo invariata la lunghezza dell'alimentato (145,0 mm), la
simulazione dà **Z ≈ 12,9 − j38,1 Ω**, cioè un ROS oltre **6** su 50 Ω: la
resistenza crolla e la reattanza cresce molto, esattamente il comportamento
descritto in [Impedenza](../guida/#impedenza). Spaziature più strette
tendono infatti ad aumentare l'accoppiamento tra gli elementi — più
guadagno e più rapporto avanti/dietro sono possibili in linea di principio,
ma solo se si accetta di dover recuperare l'impedenza con un adattamento più
aggressivo: un **gamma match** (che alza la resistenza vista dal cavo,
vedi [Adattamento](../guida/#adattamento)) insieme a un condensatore o a un
**dipolo ripiegato** (che parte da un'impedenza più alta, più comoda da
riportare a 50 Ω) invece della semplice alimentazione diretta usata qui.

**In pratica:** prima di stringere le spaziature per rincorrere più
guadagno, chiediti se sei pronto a costruire (e tarare) anche
l'adattamento che ne consegue. Questa scheda usa spaziature più larghe
apposta per restare un progetto "senza sorprese" da costruire.

Altri esperimenti:

- Confronta questa scheda con le due Yagi a 2 elementi di Fabrizio: stesso
  principio, un elemento parassita alla volta invece di due insieme. Nota
  come guadagno e F/B qui siano intermedi per il guadagno ma non superiori
  su tutti i fronti (il riflettore da solo di Fabrizio ha F/B leggermente
  migliore, 8,5 dB contro 5,9 dB): aggiungere un direttore non migliora
  sempre tutto insieme.
- Prova ad accorciare ulteriormente il direttore di qualche millimetro:
  osserva come cambiano guadagno e F/B, e a che punto l'impedenza
  dell'alimentato inizia a peggiorare.

## Errori comuni

- **Pensare che un elemento parassita più lungo dell'alimentato sia sempre
  un riflettore**: qui il direttore è più lungo solo perché l'alimentato è
  stato accorciato per compensare l'accoppiamento, come spiegato in "Come
  funziona". Quello che identifica un direttore è la sua **posizione**
  (davanti, nella direzione del massimo guadagno) insieme alla lunghezza
  **relativa** a un alimentato non accorciato, non un numero assoluto in
  millimetri.
- **Stringere le spaziature senza prevedere un adattamento**: vedi
  l'esperimento sopra — sotto certe spaziature l'impedenza crolla e serve
  un gamma match o un dipolo ripiegato, non basta più il cavo diretto.
- **Montare gli elementi orizzontali**: rompe la
  [polarizzazione verticale](../guida/#polarizzazione) della rete.

## Note

Progetto di riferimento pensato per questa galleria, per fare da ponte
didattico tra le Yagi a 2 elementi di Fabrizio e la
[Yagi a 10 elementi](../fabrizio-yagi-10el/): stessa logica additiva
(riflettore + direttori), spinta un passo alla volta.
