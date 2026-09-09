import argparse
import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANDIDATES_PATH = (
    PROJECT_ROOT / "data" / "evaluation" / "retrieval_candidates.csv"
)


def load_rows():
    with CANDIDATES_PATH.open(
        encoding="utf-8",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        return reader.fieldnames, list(reader)


def save_rows(fieldnames, rows):
    with CANDIDATES_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def ask_relevance():
    while True:
        value = input("Rilevante? [1=sì, 0=no]: ").strip()

        if value in {"0", "1"}:
            return value

        print("Inserisci soltanto 1 oppure 0.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query-id",
        required=True,
        help="Identificatore della domanda da annotare, per esempio Q001.",
    )
    args = parser.parse_args()

    fieldnames, rows = load_rows()

    selected_rows = [
        row for row in rows if row["query_id"] == args.query_id
    ]

    if not selected_rows:
        raise ValueError(f"Nessun candidato trovato per {args.query_id}")

    print(f"\nDomanda: {selected_rows[0]['question']}\n")

    for row in selected_rows:
        print("=" * 80)
        print(
            f"Rank {row['rank']} — {row['chunk_id']} "
            f"— score {row['score']}"
        )
        print(row["text_preview"])
        print()

        row["relevant"] = ask_relevance()
        row["notes"] = input("Nota breve: ").strip()

    save_rows(fieldnames, rows)
    print(f"\nAnnotazioni salvate per {args.query_id}")


if __name__ == "__main__":
    main()

