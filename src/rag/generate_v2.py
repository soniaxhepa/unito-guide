import argparse
import json
import urllib.request

from src.retrieval.search import search


OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2:3b"


def build_context(results):
    context_parts = []

    for position, result in enumerate(results, start=1):
        context_parts.append(
            f"[FONTE {position}]\n"
            f"Titolo: {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Testo:\n{result['text']}"
        )

    return "\n\n".join(context_parts)


def build_prompt(query, context):
    return f"""
Sei un assistente per l'orientamento al corso di Informatica
dell'Università di Torino.

Rispondi utilizzando esclusivamente le fonti riportate sotto.

ISTRUZIONI:
1. Leggi la domanda e individua tutte le informazioni richieste.
2. Cerca le informazioni nei testi delle fonti, anche quando
   si trovano in fonti diverse.
3. Se trovi le informazioni, rispondi direttamente e con precisione.
   Non dichiarare che mancano informazioni che sono presenti.
   Prima di terminare, controlla che la risposta includa TUTTI i dati
   richiesti dalla domanda. Se la domanda richiede due informazioni
   presenti in fonti diverse, riportale entrambe con le rispettive
   citazioni.
4. Se trovi solo una parte delle informazioni, fornisci quella parte
   e specifica chiaramente cosa non è disponibile.
5. Se la domanda è realmente ambigua, chiedi una breve precisazione.
6. Se nessuna fonte contiene le informazioni necessarie,
   dichiara che non sono disponibili nelle fonti consultate.
7. Non inventare informazioni e non utilizzare conoscenze esterne.

CITAZIONI:
- Ogni informazione fattuale deve essere accompagnata dalla fonte.
- Usa esclusivamente il formato [FONTE N].
- N deve corrispondere al numero della fonte che contiene il dato.
- Se usi due fonti, cita entrambe.
- Non citare fonti che non supportano la risposta.
- Non aggiungere citazioni inventate.

ESEMPIO DI FORMATO:
Domanda: Quanti CFU vale un insegnamento?
Risposta: L'insegnamento vale 9 CFU [FONTE 1].

Rispondi in italiano, in modo chiaro e conciso.
Non mostrare il ragionamento interno.

FONTI:
{context}

DOMANDA:
{query}

RISPOSTA:
""".strip()


def generate_answer(prompt):
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"].strip()


def main():
    parser = argparse.ArgumentParser(
        description="RAG per l'orientamento universitario."
    )
    parser.add_argument("query", help="Domanda dell'utente.")
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Numero di chunk da fornire al modello.",
    )
    args = parser.parse_args()

    results = search(args.query, args.top_k)

    context = build_context(results)
    prompt = build_prompt(args.query, context)
    answer = generate_answer(prompt)

    print("\n" + "=" * 80)
    print("DOMANDA")
    print("=" * 80)
    print(args.query)

    print("\n" + "=" * 80)
    print("RISPOSTA")
    print("=" * 80)
    print(answer)

    print("\n" + "=" * 80)
    print("FONTI RECUPERATE")
    print("=" * 80)

    for position, result in enumerate(results, start=1):
        print(
            f"[FONTE {position}] {result['title']} "
            f"(similarità: {result['score']:.4f})"
        )
        print(result["url"])


if __name__ == "__main__":
    main()
