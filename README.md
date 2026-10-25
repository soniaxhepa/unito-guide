# UniTo Guide

Prototipo di assistente conversazionale per l’orientamento al corso di
laurea in Informatica dell’Università di Torino, sviluppato nell’ambito
di una tesi di laurea.

Il progetto è indipendente e non costituisce un servizio ufficiale UniTo.
Le risposte possono contenere errori: le informazioni devono essere
verificate consultando le fonti ufficiali.

## Funzionamento

Il sistema adotta un’architettura Retrieval-Augmented Generation (RAG).
Per ogni domanda recupera cinque passaggi dai documenti indicizzati
e li fornisce a un modello linguistico come contesto per generare
la risposta.

La configurazione principale utilizza:

- interfaccia web realizzata con Streamlit;
- modello di embedding `intfloat/multilingual-e5-small`, eseguito su CPU;
- ricerca semantica basata sulla similarità tra embedding;
- modello generativo `llama3.2:3b`, eseguito localmente tramite Ollama;
- temperatura di generazione pari a `0.2`;
- cinque passaggi recuperati per domanda.

Il corpus comprende sei pagine ufficiali in italiano, selezionate
dal portale dell’Università di Torino e dal sito del corso di laurea.
I documenti riguardano informazioni amministrative e didattiche,
tra cui accesso, iscrizioni, insegnamenti e calendario didattico.

L’interfaccia permette di formulare domande, leggere le risposte
e consultare i passaggi recuperati con i collegamenti alle fonti.
Ogni domanda viene elaborata separatamente, senza memoria
delle richieste precedenti.

## Requisiti

Per utilizzare il prototipo servono:

- Python e le dipendenze del progetto;
- Ollama installato e in esecuzione;
- il modello `llama3.2:3b`;
- il modello di embedding, scaricato attraverso Sentence Transformers.

I pesi dei modelli e l’ambiente Python non sono inclusi nel repository.

Gli esperimenti descritti nella tesi sono stati eseguiti su un Mac
con 8 GB di RAM, utilizzando Python 3.12.

## Installazione e avvio

Dalla cartella principale del progetto, preferibilmente in un ambiente
Python dedicato, installare le dipendenze:

    python3 -m pip install -r frontend/requirements.txt

Scaricare il modello generativo:

    ollama pull llama3.2:3b

Avviare Ollama e, dalla cartella principale del progetto, eseguire:

    make run

Aprire nel browser l’indirizzo mostrato nel terminale e lasciare
il processo in esecuzione.

Se `make` non è disponibile, utilizzare:

    python3 -m streamlit run frontend/app.py --server.address 127.0.0.1 --server.fileWatcherType none

Il primo utilizzo può richiedere il download del modello di embedding.
Le modifiche al codice richiedono il riavvio dell’applicazione.

Ulteriori indicazioni sono disponibili in
[frontend/DEMO.md](frontend/DEMO.md).

## Struttura del progetto

- `frontend/`: interfaccia Streamlit.
- `src/ingestion/`: acquisizione delle pagine, estrazione del testo
  e suddivisione in passaggi.
- `src/retrieval/`: costruzione dell’indice e recupero dei passaggi.
- `src/rag/`: costruzione del contesto, preparazione del prompt
  e generazione delle risposte.
- `src/evaluation/`: strumenti utilizzati durante la valutazione
  e lo sviluppo.
- `data/sources/`: descrizione delle fonti e controlli di integrità.
- `data/raw/html/`: copia delle pagine HTML acquisite.
- `data/processed/`: testi estratti, passaggi e indice locale.
- `data/evaluation/`: domande, risposte, valutazioni ed esperimenti.

## Corpus e indice locale

Il repository conserva una copia dei sei documenti HTML acquisiti,
dei testi estratti, dei passaggi e dell’indice locale.

L’indice comprende:

- `embeddings.npy`: matrice degli embedding;
- `metadata.jsonl`: testi e metadati associati ai vettori;
- `manifest.json`: configurazione dell’indice.

Gli hash SHA-256 del corpus conservato sono disponibili in:

    data/sources/corpus_snapshot_sha256.txt

Gli hash permettono di rilevare modifiche ai file. Non verificano
l’aggiornamento delle informazioni rispetto alle pagine online
e non certificano, da soli, l’identità con i materiali
dell’esperimento iniziale.

Non è necessario riscaricare le pagine o ricostruire l’indice
per utilizzare la copia inclusa nel repository.
La rigenerazione può sovrascrivere i dati conservati:
è opportuno eseguire eventuali prove in una cartella separata.

## Protocollo di valutazione

Durante lo sviluppo sono state utilizzate 23 domande preliminari.
Per la valutazione è stato predisposto un insieme separato
di 40 domande:

| Comportamento atteso | Domande |
|---|---:|
| Risposta informativa | 32 |
| Richiesta di chiarimento | 4 |
| Astensione per informazioni insufficienti | 4 |
| Totale | 40 |

Il confronto riguarda due configurazioni dello stesso modello:

- **RAG:** il modello riceve i passaggi recuperati e le istruzioni
  per utilizzarli.
- **No-RAG:** il modello risponde senza recupero documentale.

Entrambe utilizzano `llama3.2:3b` con temperatura `0.2`.

La raccolta comprende un esperimento iniziale di 80 risposte
e tre esecuzioni successive, per ulteriori 240 risposte.
Complessivamente sono state raccolte 320 risposte
alle stesse 40 domande.

I risultati delle due fasi sono presentati separatamente.

Correttezza e completezza sono valutate su una scala da 0 a 2.
Sono esaminati anche il supporto documentale, le citazioni,
le affermazioni non supportate e le astensioni.

I giudizi sono stati preparati, controllati e confermati manualmente dall’autrice.
Non è stata svolta una seconda valutazione indipendente.

Alcune domande della valutazione sono state riutilizzate
nelle prove esplorative prima delle tre esecuzioni successive.
I risultati non rappresentano quindi una verifica su domande
completamente nuove rispetto alla scelta delle varianti.

## Esperimento iniziale

L’esperimento iniziale comprende 40 risposte per configurazione.

| Correttezza | RAG | No-RAG |
|---|---:|---:|
| Pienamente corretta | 45,00% | 10,00% |
| Parzialmente corretta | 17,50% | 15,00% |
| Errata o non adeguata | 37,50% | 75,00% |

Il punteggio medio di correttezza, sulla scala 0–2,
è pari a 1,075 con RAG e 0,350 senza RAG.

Il tempo medio registrato è di 26,89 secondi con RAG
e 6,95 secondi senza RAG.

I principali file di questa fase si trovano in `data/evaluation/`:

- `final_test_questions_FROZEN.csv`
- `final_test_generation_comparison.csv`
- `final_test_manual_evaluation.csv`
- `final_test_retrieval_candidates.csv`
- `final_test_retrieval_metrics.json`

Il file `final_test_sha256.txt` conserva l’hash storico del dataset.
Le copie e le revisioni storiche sono mantenute separatamente.

## Tre esecuzioni successive

Le stesse 40 domande sono state sottoposte alle due configurazioni
in tre esecuzioni successive, raccogliendo 240 risposte:
120 con RAG e 120 senza RAG.

| Correttezza | RAG | No-RAG |
|---|---:|---:|
| Pienamente corretta | 34,17% | 12,50% |
| Parzialmente corretta | 28,33% | 16,67% |
| Errata o non adeguata | 37,50% | 70,83% |

Le percentuali di risposte pienamente corrette nelle singole
esecuzioni sono:

| Esecuzione | RAG | No-RAG |
|---|---:|---:|
| 1 | 35,00% | 15,00% |
| 2 | 37,50% | 10,00% |
| 3 | 30,00% | 12,50% |
| Media | 34,17% | 12,50% |
| Deviazione standard campionaria | 3,82 p.p. | 2,50 p.p. |

La deviazione standard descrive la variabilità tra le tre percentuali
ed è espressa in punti percentuali. Non costituisce un intervallo
di confidenza.

I punteggi medi sulla scala 0–2 sono:

| Indicatore | RAG | No-RAG |
|---|---:|---:|
| Correttezza | 0,967 | 0,417 |
| Completezza | 1,050 | 0,417 |

### Risultati per comportamento atteso

| Comportamento atteso | Risposte per modalità | Pienamente corrette RAG | Pienamente corrette No-RAG |
|---|---:|---:|---:|
| Risposta informativa | 96 | 33 (34,38%) | 0 (0,00%) |
| Chiarimento | 12 | 0 (0,00%) | 3 (25,00%) |
| Astensione | 12 | 8 (66,67%) | 12 (100,00%) |

Il vantaggio osservato del RAG riguarda soprattutto le domande
informative. Le risposte pienamente corrette del No-RAG provengono
dai casi di chiarimento e astensione.

Le categorie di chiarimento e astensione comprendono pochi casi:
le relative percentuali devono essere interpretate considerando
questa limitazione.

### Fonti e citazioni

Nelle tre esecuzioni:

- l’aderenza media alle fonti del RAG è pari a 1,042 su 2;
- 12 risposte RAG su 120, pari al 10%, soddisfano i criteri
  della valutazione delle citazioni;
- almeno un’affermazione non supportata compare in 72 risposte
  RAG su 120 e in 57 risposte No-RAG su 120.

Il controllo delle citazioni considera anche formato e pertinenza.
Il mancato superamento di tale controllo non implica automaticamente
che tutte le informazioni della risposta siano false.

Le percentuali di affermazioni non supportate indicano la quota
di risposte che ne contengono almeno una, non la percentuale
di singole affermazioni false.

## Tempi di elaborazione

Le tre esecuzioni successive comprendono 120 misure per modalità.

| Indicatore | RAG | No-RAG |
|---|---:|---:|
| Tempo medio | 34,19 s | 8,48 s |
| Mediana | 33,09 s | 6,41 s |
| Deviazione standard campionaria dei tempi | 11,07 s | 6,11 s |

Il tempo medio complessivo del RAG è circa quattro volte
quello del No-RAG.

Per il RAG, la misura comprende il recupero dei passaggi,
la preparazione del prompt e la generazione.
Per il No-RAG comprende la preparazione del prompt
e la generazione.

Sono incluse le eventuali operazioni di caricamento dei modelli.
Il salvataggio dei risultati su disco è escluso dalle misure
delle tre esecuzioni successive.

Le singole fasi non sono state cronometrate separatamente:
la differenza non può essere attribuita al solo recupero.
Le richieste sono state eseguite nell’ordine RAG/No-RAG,
senza separare sistematicamente primo caricamento e modelli
già presenti in memoria.

La deviazione standard dei tempi è calcolata sulle 120 misure
per modalità ed è distinta dalla deviazione standard
delle percentuali di correttezza tra le tre esecuzioni.

## Esperimenti esplorativi

Il progetto comprende prove su modifiche al prompt,
ricerca ibrida e un modello generativo alternativo.

- `src/rag/generate_v1.py` conserva una copia del generatore originale.
- `src/rag/generate_v2.py` introduce modifiche al prompt.
- `src/retrieval/search_hybrid.py` combina ricerca semantica e BM25.
- Gli output esplorativi sono conservati in
  `data/evaluation/experimental/`.

Sulle 32 domande informative, il confronto del recupero
nei primi cinque risultati ha prodotto:

| Condizione | Ricerca semantica | Ricerca ibrida |
|---|---:|---:|
| Almeno un riferimento atteso recuperato | 28/32 (87,50%) | 31/32 (96,88%) |
| Tutti i riferimenti attesi recuperati | 26/32 (81,25%) | 29/32 (90,63%) |

Le due condizioni non sono categorie da sommare.
Questi risultati riguardano il recupero dei riferimenti,
non la correttezza delle risposte generate.

Le prove di generazione, comprese quelle con `qwen2.5:3b`,
non mostrano un miglioramento sistematico delle risposte.
Le varianti esplorative non sono utilizzate nell’applicazione
principale e non costituiscono test indipendenti.

## Riproducibilità

Il repository conserva i materiali dell’esperimento iniziale.
Per le tre esecuzioni successive, i materiali locali comprendono:

    data/evaluation/repeated/20261020_031238_317241/

La cartella contiene richieste, risposte, prompt, configurazione,
informazioni sull’ambiente e una copia dei materiali utilizzati.

Il file `manual_evaluation.csv` prodotto dalla procedura di raccolta
è un modello da compilare e non costituisce, da solo,
la valutazione finale confermata.

La valutazione confermata delle 240 risposte è conservata nel file:

    valutazione_manuale_confermata_240.csv

Il relativo riepilogo è:

    riepilogo_manuale_confermato.csv

Nei risultati confermati, le colonne `final_*` identificano
i giudizi da utilizzare per i calcoli. Le colonne delle proposte
o delle valutazioni storiche non devono essere confuse
con quelle finali.

I prompt completi dell’esperimento iniziale non sono conservati.
Per le tre esecuzioni successive sono invece disponibili
i prompt e i log delle richieste e delle risposte.

La disponibilità dei materiali non garantisce di riprodurre
esattamente le risposte: la generazione può variare
e le dipendenze dell’applicazione non sono interamente congelate.

`src/evaluation/compare_generation.py` riguarda le prove
di sviluppo e non rigenera automaticamente il test finale.

## Limiti

Il prototipo può:

- non recuperare il passaggio necessario;
- interpretare in modo scorretto informazioni presenti nel contesto;
- collegare condizioni che riguardano situazioni diverse;
- attribuire informazioni a fonti non pertinenti;
- produrre affermazioni non supportate;
- gestire in modo inadeguato richieste ambigue.

La presenza di un passaggio tra i risultati recuperati non garantisce
che il modello lo utilizzi correttamente.
Il punteggio di similarità riguarda il recupero e non rappresenta
la probabilità che la risposta sia corretta.

La valutazione utilizza un corpus ristretto e domande costruite
durante il progetto. Non è stato svolto uno studio con studenti
né un confronto tra annotazioni indipendenti.

È stata inoltre individuata un’incoerenza tra un passaggio escluso
dall’indice e un riferimento atteso dal dataset.
La coerenza tra documenti, indice e valutazione richiede
quindi controlli espliciti.

I risultati descrivono il campione e la configurazione esaminati
e non dimostrano l’affidabilità del sistema per un impiego autonomo
nell’orientamento universitario.

## Sviluppi futuri

Le principali direzioni di sviluppo riguardano:

- controlli di coerenza tra documenti, indice e dataset;
- verifica del supporto documentale delle affermazioni;
- valutazione su nuove domande, separate dalla scelta delle modifiche;
- misurazione distinta delle fasi di elaborazione;
- valutazioni indipendenti e prove con studenti;
- aggiornamento controllato delle fonti.

L’ampliamento del corpus e l’adozione di modelli o configurazioni
alternative richiedono ulteriori verifiche.

## Licenza

Il codice originale del progetto è distribuito con licenza MIT.
Il testo completo è disponibile nel file [LICENSE](LICENSE).

La licenza MIT del progetto non si applica ai contenuti
delle pagine UniTo, ai testi e ai dati da esse derivati,
al logo dell’Università di Torino, ai modelli
o agli altri materiali di terzi.

Questi materiali restano soggetti ai diritti e alle condizioni
dei rispettivi titolari.
