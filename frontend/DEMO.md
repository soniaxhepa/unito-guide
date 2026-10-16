# UniTo Guide — guida alla demo

## Avvio
Aprire Ollama, poi eseguire nel terminale, un comando alla volta:
    conda activate unito-guide
    cd ~/HCI-STAGE
    python3 -m streamlit run frontend/app.py --server.address 127.0.0.1 --server.fileWatcherType none

Aprire l'indirizzo mostrato dal terminale.
Lasciare il terminale aperto. Per arrestare l'app: Ctrl+C.
Controllare lo stato di Ollama nella barra laterale.

## Sistema nell'interfaccia
Generatore attuale: generate.py con llama3.2:3b, temperatura 0,2.
Recupero originale, cinque passaggi fissi.
Ricerca ibrida e Qwen restano esperimenti separati.

## Esempi osservati in precedenza con la v2
Gli esiti seguenti non sono verifiche del generatore originale attuale.
1. Quale TOLC serve per iscriversi a Informatica?
Osservato: TOLC-S, con citazione verificata.

2. Qual è il punteggio minimo di matematica per superare il TOLC-S
e cosa succede se non lo raggiungo?
Osservato: 5/20 in Matematica di base e OFA entro il primo anno.
Contenuto supportato dal passaggio; citazione assente nella risposta.

3. È possibile ripetere il medesimo tipo di test CISIA
due volte nello stesso mese?
Osservato: risposta affermativa errata.
Aprire la fonte: specifica non più di una volta al mese.

Le risposte possono variare tra esecuzioni.
Verificare le citazioni nella richiesta corrente.

## Valutazione manuale salvata: 40 domande per modalità
RAG: 18 corrette (45%), 7 parziali (17,5%), 15 errate (37,5%).
Senza RAG: 4 corrette (10%), 6 parziali (15%), 30 errate (75%).
Questi numeri non sono una valutazione verificata della v2 web.

## Ricerca ibrida: confronto esplorativo su 32 domande
Almeno un riferimento atteso nei primi cinque:
originale 28/32 (87,5%); ibrida 31/32 (96,9%).
Tutti i riferimenti attesi nei primi cinque:
originale 26/32 (81,25%); ibrida 29/32 (90,625%).
Queste misure riguardano il recupero, non le risposte corrette.
Il dataset era già stato analizzato: non è un test indipendente.

## Esito degli esperimenti
La migliore copertura non ha prodotto risposte affidabilmente migliori.
Qwen non ha mostrato un vantaggio convincente sui sei casi provati.
Aumentare il contesto a 8192 token non ha risolto Q045 con Qwen.
Output separati in data/evaluation/experimental/.
Originali, indice e risultati precedenti non sono stati modificati.

## Messaggio per la relatrice
Il prototipo web è operativo. Il RAG migliora rispetto al modello
senza recupero nella valutazione salvata, ma resta inaffidabile
su alcuni casi. La ricerca ibrida migliora il recupero delle fonti;
la fedeltà della generazione richiede ulteriore lavoro.

## Allineamento dell'interfaccia al generatore originale
L'interfaccia importa ora src.rag.generate e usa cinque passaggi fissi.
generate.py e la copia generate_v1.py risultano identici.
Le 40 righe RAG dell'esperimento finale registrano llama3.2:3b,
temperatura 0,2 e top_k=5, coincidenti con la configurazione attuale.
Non è stata recuperata una registrazione completa del codice e
dell'ambiente dell'esecuzione finale: l'identità esatta resta da confermare.

Prova web dopo il collegamento al generatore originale:
alla domanda sul TOLC per Informatica risponde TOLC-S, indicando Fonte 3.
Il formato della citazione non rispetta [FONTE N].
L'espansione aggiunta del nome del test non è stata verificata nella fonte.
Le prove precedenti con v2 restano separate da questa verifica.
