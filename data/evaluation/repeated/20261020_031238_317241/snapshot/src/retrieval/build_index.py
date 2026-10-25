import csv
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"
EXCLUSIONS_PATH = (
    PROJECT_ROOT / "data" / "evaluation" / "chunk_exclusions.csv"
)
INDEX_DIRECTORY = PROJECT_ROOT / "data" / "processed" / "index"

EMBEDDINGS_PATH = INDEX_DIRECTORY / "embeddings.npy"
METADATA_PATH = INDEX_DIRECTORY / "metadata.jsonl"
MANIFEST_PATH = INDEX_DIRECTORY / "manifest.json"

MODEL_NAME = "intfloat/multilingual-e5-small"


def load_chunks():
    """Carica i chunk prodotti dalla pipeline di ingestion."""
    with CHUNKS_PATH.open(encoding="utf-8") as input_file:
        return [json.loads(line) for line in input_file if line.strip()]


def load_excluded_chunk_ids():
    """Carica gli identificatori esclusi durante la revisione manuale."""
    if not EXCLUSIONS_PATH.exists():
        return set()

    with EXCLUSIONS_PATH.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return {
            row["chunk_id"].strip()
            for row in reader
            if row.get("chunk_id", "").strip()
        }


def save_metadata(chunks):
    """Salva i metadati nello stesso ordine degli embeddings."""
    with METADATA_PATH.open("w", encoding="utf-8") as output_file:
        for chunk in chunks:
            output_file.write(
                json.dumps(chunk, ensure_ascii=False) + "\n"
            )


def main():
    INDEX_DIRECTORY.mkdir(parents=True, exist_ok=True)

    chunks = load_chunks()
    excluded_ids = load_excluded_chunk_ids()

    available_ids = {chunk["chunk_id"] for chunk in chunks}
    unknown_exclusions = excluded_ids - available_ids

    if unknown_exclusions:
        raise ValueError(
            "Esclusioni riferite a chunk inesistenti: "
            + ", ".join(sorted(unknown_exclusions))
        )

    approved_chunks = [
        chunk
        for chunk in chunks
        if chunk["chunk_id"] not in excluded_ids
    ]

    if not approved_chunks:
        raise ValueError("Nessun chunk approvato da indicizzare.")

    passages = [
        f"passage: {chunk['text']}"
        for chunk in approved_chunks
    ]

    print(f"Modello: {MODEL_NAME}")
    print(f"Chunk disponibili: {len(chunks)}")
    print(f"Chunk esclusi: {len(excluded_ids)}")
    print(f"Chunk da indicizzare: {len(approved_chunks)}")

    model = SentenceTransformer(MODEL_NAME, device="cpu")

    embeddings = model.encode(
        passages,
        batch_size=8,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    np.save(EMBEDDINGS_PATH, embeddings)
    save_metadata(approved_chunks)

    manifest = {
        "model_name": MODEL_NAME,
        "document_prefix": "passage: ",
        "query_prefix": "query: ",
        "normalized_embeddings": True,
        "chunk_count": len(approved_chunks),
        "excluded_chunk_ids": sorted(excluded_ids),
        "embedding_dimension": int(embeddings.shape[1]),
    }

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\nForma embeddings: {embeddings.shape}")
    print(f"Embeddings salvati in: {EMBEDDINGS_PATH}")
    print(f"Metadati salvati in: {METADATA_PATH}")
    print(f"Manifest salvato in: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()

