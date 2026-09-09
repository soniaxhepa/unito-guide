import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_DIRECTORY = PROJECT_ROOT / "data" / "processed" / "index"

EMBEDDINGS_PATH = INDEX_DIRECTORY / "embeddings.npy"
METADATA_PATH = INDEX_DIRECTORY / "metadata.jsonl"
MANIFEST_PATH = INDEX_DIRECTORY / "manifest.json"


def load_metadata():
    with METADATA_PATH.open(encoding="utf-8") as input_file:
        return [json.loads(line) for line in input_file if line.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Ricerca semantica nel corpus UniTO Guide."
    )
    parser.add_argument("query", help="Domanda da cercare nel corpus.")
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Numero di risultati da mostrare.",
    )
    args = parser.parse_args()

    embeddings = np.load(EMBEDDINGS_PATH)
    metadata = load_metadata()
    manifest = json.loads(
        MANIFEST_PATH.read_text(encoding="utf-8")
    )

    if len(metadata) != len(embeddings):
        raise ValueError(
            "Il numero di record non corrisponde al numero di embeddings."
        )

    model = SentenceTransformer(
        manifest["model_name"],
        device="cpu",
    )

    query_text = f"{manifest['query_prefix']}{args.query}"

    query_embedding = model.encode(
        query_text,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    scores = embeddings @ query_embedding

    top_k = min(args.top_k, len(metadata))
    result_indices = np.argsort(scores)[::-1][:top_k]

    print(f"\nDomanda: {args.query}")
    print(f"Risultati recuperati: {top_k}\n")

    for position, index in enumerate(result_indices, start=1):
        record = metadata[index]
        score = float(scores[index])

        print("=" * 80)
        print(
            f"{position}. {record['chunk_id']} "
            f"— similarità: {score:.4f}"
        )
        print(f"Titolo: {record['title']}")
        print(f"Argomento: {record['topic']}")
        print(f"Fonte: {record['url']}")
        print()
        print(record["text"])
        print()


if __name__ == "__main__":
    main()

