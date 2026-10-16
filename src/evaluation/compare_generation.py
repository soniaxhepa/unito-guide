import csv
import json
import time
from pathlib import Path

from src.rag.generate import (
    build_context,
    build_prompt,
    generate_answer,
)
from src.retrieval.search import search

ROOT = Path(__file__).resolve().parents[2]
QUESTIONS = ROOT / "data/evaluation/retrieval_questions.csv"
OUTPUT = ROOT / "data/evaluation/generation_comparison.csv"

TOP_K = 5

NO_RAG_PROMPT = """
Sei un assistente per l'orientamento universitario.

Rispondi alla domanda usando le conoscenze a tua disposizione.
Non inventare informazioni.
Se non conosci la risposta, dichiara che non hai informazioni sufficienti.
Rispondi in italiano, in modo chiaro e conciso.

DOMANDA:
{question}

RISPOSTA:
""".strip()


def main():
    with QUESTIONS.open(encoding="utf-8-sig", newline="") as f:
        questions = [
            row for row in csv.DictReader(f)
            if row["split"] == "development"
        ]

    fieldnames = [
        "query_id", "mode", "question", "answer",
        "retrieved_chunks", "latency_seconds",
        "model", "temperature", "top_k"
    ]

    existing = set()

    if OUTPUT.exists():
        with OUTPUT.open(encoding="utf-8", newline="") as f:
            existing = {
                (row["query_id"], row["mode"])
                for row in csv.DictReader(f)
            }

    with OUTPUT.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if OUTPUT.stat().st_size == 0:
            writer.writeheader()

        for question in questions:
            qid = question["query_id"]
            query = question["question"]

            for mode in ("rag", "no_rag"):
                if (qid, mode) in existing:
                    continue

                print(f"\n{qid} | {mode}", flush=True)

                start = time.perf_counter()

                if mode == "rag":
                    results = search(query, TOP_K)
                    context = build_context(results)
                    prompt = build_prompt(query, context)
                    chunks = [r["chunk_id"] for r in results]
                else:
                    prompt = NO_RAG_PROMPT.format(question=query)
                    chunks = []

                answer = generate_answer(prompt)
                elapsed = time.perf_counter() - start

                writer.writerow({
                    "query_id": qid,
                    "mode": mode,
                    "question": query,
                    "answer": answer,
                    "retrieved_chunks": json.dumps(chunks),
                    "latency_seconds": round(elapsed, 3),
                    "model": "llama3.2:3b",
                    "temperature": 0.2,
                    "top_k": TOP_K if mode == "rag" else 0,
                })
                f.flush()

                print(f"Tempo: {elapsed:.1f}s")
                print(f"Risposta: {answer[:180]}")

    print(f"\nEsperimento completato. Risultati: {OUTPUT}")


if __name__ == "__main__":
    main()
