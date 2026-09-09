import csv
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

QUESTIONS_PATH = (
    PROJECT_ROOT / "data" / "evaluation" / "retrieval_questions.csv"
)
INDEX_DIRECTORY = PROJECT_ROOT / "data" / "processed" / "index"
EMBEDDINGS_PATH = INDEX_DIRECTORY / "embeddings.npy"
METADATA_PATH = INDEX_DIRECTORY / "metadata.jsonl"
MANIFEST_PATH = INDEX_DIRECTORY / "manifest.json"

OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "evaluation" / "retrieval_candidates.csv"
)

TOP_K = 5


def load_questions():
    with QUESTIONS_PATH.open(encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def load_metadata():
    with METADATA_PATH.open(encoding="utf-8") as input_file:
        return [json.loads(line) for line in input_file if line.strip()]


def main():
    questions = load_questions()
    metadata = load_metadata()
    embeddings = np.load(EMBEDDINGS_PATH)

    manifest = json.loads(
        MANIFEST_PATH.read_text(encoding="utf-8")
    )

    if len(metadata) != len(embeddings):
        raise ValueError(
            "Metadati ed embeddings hanno lunghezze differenti."
        )

    model = SentenceTransformer(
        manifest["model_name"],
        device="cpu",
    )

    query_texts = [
        f"{manifest['query_prefix']}{question['question']}"
        for question in questions
    ]

    query_embeddings = model.encode(
        query_texts,
        batch_size=8,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    rows = []

    for question, query_embedding in zip(
        questions,
        query_embeddings,
        strict=True,
    ):
        scores = embeddings @ query_embedding
        result_indices = np.argsort(scores)[::-1][:TOP_K]

        for rank, index in enumerate(result_indices, start=1):
            record = metadata[index]
            preview = record["text"].replace("\n", " ")

            rows.append(
                {
                    "query_id": question["query_id"],
                    "question": question["question"],
                    "rank": rank,
                    "chunk_id": record["chunk_id"],
                    "source_id": record["source_id"],
                    "score": f"{float(scores[index]):.6f}",
                    "text_preview": preview,
                    "relevant": "",
                    "notes": "",
                }
            )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as output_file:
        fieldnames = [
            "query_id",
            "question",
            "rank",
            "chunk_id",
            "source_id",
            "score",
            "text_preview",
            "relevant",
            "notes",
        ]

        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Domande elaborate: {len(questions)}")
    print(f"Candidati per domanda: {TOP_K}")
    print(f"Righe prodotte: {len(rows)}")
    print(f"File salvato in: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

