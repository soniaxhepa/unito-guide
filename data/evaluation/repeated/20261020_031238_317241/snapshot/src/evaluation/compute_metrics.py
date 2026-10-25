import csv
import json
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CANDIDATES_PATH = (
    PROJECT_ROOT / "data" / "evaluation" / "retrieval_candidates.csv"
)

RESULTS_CSV_PATH = (
    PROJECT_ROOT / "data" / "evaluation" / "retrieval_metrics_by_query.csv"
)

SUMMARY_JSON_PATH = (
    PROJECT_ROOT / "data" / "evaluation" / "retrieval_metrics_summary.json"
)


def load_candidates():
    with CANDIDATES_PATH.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("Il file dei candidati è vuoto.")

    missing = [
        row
        for row in rows
        if row.get("relevant", "").strip() not in {"0", "1"}
    ]

    if missing:
        query_ids = sorted({row["query_id"] for row in missing})
        raise ValueError(
            "Annotazioni mancanti o non valide per: "
            + ", ".join(query_ids)
        )

    return rows


def calculate_metrics(rows):
    grouped = defaultdict(list)

    for row in rows:
        grouped[row["query_id"]].append(row)

    results = []

    for query_id, candidates in sorted(grouped.items()):
        candidates.sort(key=lambda row: int(row["rank"]))

        relevant_ranks = [
            int(row["rank"])
            for row in candidates
            if row["relevant"].strip() == "1"
        ]

        first_relevant_rank = min(relevant_ranks) if relevant_ranks else None

        result = {
            "query_id": query_id,
            "question": candidates[0]["question"],
            "first_relevant_rank": first_relevant_rank or "",
            "recall_at_1": int(
                any(rank <= 1 for rank in relevant_ranks)
            ),
            "recall_at_3": int(
                any(rank <= 3 for rank in relevant_ranks)
            ),
            "recall_at_5": int(
                any(rank <= 5 for rank in relevant_ranks)
            ),
            "reciprocal_rank": (
                1 / first_relevant_rank if first_relevant_rank else 0.0
            ),
        }

        results.append(result)

    return results


def calculate_summary(results):
    query_count = len(results)

    return {
        "query_count": query_count,
        "recall_at_1": sum(
            row["recall_at_1"] for row in results
        ) / query_count,
        "recall_at_3": sum(
            row["recall_at_3"] for row in results
        ) / query_count,
        "recall_at_5": sum(
            row["recall_at_5"] for row in results
        ) / query_count,
        "mrr": sum(
            row["reciprocal_rank"] for row in results
        ) / query_count,
    }


def save_results(results, summary):
    fieldnames = [
        "query_id",
        "question",
        "first_relevant_rank",
        "recall_at_1",
        "recall_at_3",
        "recall_at_5",
        "reciprocal_rank",
    ]

    with RESULTS_CSV_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    SUMMARY_JSON_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    rows = load_candidates()
    results = calculate_metrics(rows)
    summary = calculate_summary(results)

    save_results(results, summary)

    print(f"Domande valutate: {summary['query_count']}")
    print(f"Recall@1: {summary['recall_at_1']:.3f}")
    print(f"Recall@3: {summary['recall_at_3']:.3f}")
    print(f"Recall@5: {summary['recall_at_5']:.3f}")
    print(f"MRR:      {summary['mrr']:.3f}")

    print("\nPrimo risultato rilevante per domanda:")

    for row in results:
        rank = row["first_relevant_rank"] or "nessuno"
        print(f"{row['query_id']}: rank {rank}")

    print(f"\nDettaglio salvato in: {RESULTS_CSV_PATH}")
    print(f"Riepilogo salvato in: {SUMMARY_JSON_PATH}")


if __name__ == "__main__":
    main()
