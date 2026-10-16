# UniTo Guide

Prototipo di tesi per l'orientamento a Informatica, Università di Torino.
Progetto di ricerca indipendente, non un servizio ufficiale UniTo.

## Sistema attuale
Interfaccia Streamlit con domanda, risposta, fonti e stato di Ollama.
Generatore: src/rag/generate.py con llama3.2:3b e temperatura 0,2.
Ricerca semantica originale, cinque passaggi fissi per domanda.
Embedding: intfloat/multilingual-e5-small su CPU.
Ogni domanda è indipendente: non c'è memoria conversazionale.
Il corpus locale verificato comprende sei pagine e 22 passaggi.

## Avvio
Dalla cartella del progetto, nell'ambiente Python:
    python3 -m pip install -r frontend/requirements.txt
    ollama pull llama3.2:3b

Aprire Ollama. Dalla cartella del progetto, con l'ambiente attivo:
    make run

Aprire l'indirizzo mostrato e lasciare il terminale attivo.
Le modifiche al codice richiedono il riavvio.
Ulteriori istruzioni: frontend/DEMO.md.

## Dati e riproducibilità
Il repository include una copia dei sei documenti HTML acquisiti,
dei testi estratti, dei chunk e dell'indice locale.
Sono inclusi 16 file specifici; altri dati generati restano esclusi.

Gli hash SHA-256 sono in data/sources/corpus_snapshot_sha256.txt.
Descrivono la copia locale conservata durante questo aggiornamento,
non certificano l'identità con il corpus dell'esperimento storico.

Non è necessario riscaricare le pagine o ricostruire l'indice
per utilizzare questa copia. La rigenerazione può sovrascriverla:
eseguire eventuali prove in una cartella separata.

I modelli e l'ambiente Python non sono inclusi.
Servono Python compatibile, dipendenze, Ollama e llama3.2:3b.
Il modello di embedding può richiedere un download al primo utilizzo.
Le dipendenze non sono interamente congelate: la riproduzione
esatta delle risposte storiche non è garantita.

Il comando make run richiede anche il programma make.
Se make non è disponibile, dalla cartella del progetto usare:
    python3 -m streamlit run frontend/app.py --server.address 127.0.0.1 --server.fileWatcherType none

## Valutazione finale salvata
40 domande, 80 risposte: 40 RAG e 40 senza RAG.
Verificata la corrispondenza tra domande, risposte e valutazioni.

| Correttezza | RAG | Senza RAG |
|---|---:|---:|
| Completa | 45% | 10% |
| Parziale | 17,5% | 15% |
| Nulla | 37,5% | 75% |

Correttezza media su 2: RAG 1,075; senza RAG 0,350.
Tempo medio registrato: RAG 26,894 s; senza RAG 6,952 s.
Deviazione standard campionaria dei tempi: 4,492 s e 4,476 s.
La variabilità è tra domande, non tra ripetizioni della stessa domanda.

File principali in data/evaluation:
- final_test_questions_FROZEN.csv
- final_test_generation_comparison.csv
- final_test_manual_evaluation.csv
- final_test_retrieval_candidates.csv
- final_test_retrieval_metrics.json

Il file final_test_sha256.txt conserva l'hash storico del dataset.
.gitattributes impedisce conversioni dei fine riga nei dati di valutazione.
Le copie e revisioni storiche sono conservate separatamente.

## Esperimenti esplorativi
generate_v1.py conserva una copia del generatore originale.
generate_v2.py modifica il prompt.
search_hybrid.py combina ricerca semantica e BM25.
Gli output successivi sono in data/evaluation/experimental/.
Su 32 domande, almeno un riferimento atteso nei primi cinque:
originale 28/32; ibrida 31/32. Tutti i riferimenti: 26/32 e 29/32.
Sono risultati sul recupero, non percentuali di risposte corrette.
Le prove di generazione e con Qwen non dimostrano miglioramenti affidabili.
Queste varianti non sono usate nell'app e non sono test indipendenti.

## Limiti
Il modello può interpretare male fonti corrette o citarle erroneamente.
Non è stato svolto uno studio di usabilità con studenti.
L'app usa il generatore originale conservato e i parametri del CSV finale.
I prompt storici non sono salvati: l'identità esatta della configurazione
dell'esperimento finale non è stata certificata.
compare_generation.py riguarda lo sviluppo, non rigenera il test finale.
I risultati descrivono le risposte conservate e valutate.
