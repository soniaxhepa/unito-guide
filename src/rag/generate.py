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
Sei un assistente per l'orientamento universitario.

Rispondi alla domanda utilizzando esclusivamente le informazioni
esplicitamente contenute nelle fonti fornite.

Regole:
- Non utilizzare conoscenze esterne alle fonti.
- Non inventare, dedurre o completare informazioni mancanti.
- Verifica che le fonti contengano effettivamente l'informazione richiesta
  dalla domanda, non soltanto informazioni sullo stesso argomento.
- Se le fonti sono pertinenti all'argomento ma non contengono la risposta
  richiesta, rispondi che le informazioni disponibili non sono sufficienti.
- Non trasformare categorie, sezioni o informazioni correlate in una
  risposta se le fonti non le identificano esplicitamente come ciò che
  viene richiesto.
- Rispondi in italiano.
- Sii chiaro e conciso.
- Quando utilizzi un'informazione, indica la fonte nel formato [FONTE N].

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
