"""Recupero sperimentale: ricerca semantica + BM25 con fusione RRF."""
import math
import re
from collections import Counter

from src.retrieval.search import load_metadata, search as semantic_search

STOPWORDS = set("""
a ad al alla alle ai agli anche che chi con da dal dalla dei del
della delle di e è gli i il in la le lo ma mi nel nella o per
quale quali quanto se sono su un una uno devo posso voglio
""".split())


def tokenize(text):
    words = re.findall(r"[^\W_]+(?:-[^\W_]+)*", text.casefold())
    return [word for word in words if word not in STOPWORDS]


def search(query, top_k=5):
    if top_k < 1:
        raise ValueError("top_k deve essere almeno 1.")

    metadata = load_metadata()
    if not metadata:
        return []

    ids = [record["chunk_id"] for record in metadata]
    if len(set(ids)) != len(ids):
        raise ValueError("Gli identificativi dei passaggi non sono univoci.")

    documents = [
        Counter(tokenize(record.get("title", "") + " " + record["text"]))
        for record in metadata
    ]
    lengths = [sum(document.values()) for document in documents]
    average_length = sum(lengths) / len(lengths) or 1
    document_frequency = Counter()
    for document in documents:
        document_frequency.update(document.keys())

    query_terms = set(tokenize(query))
    lexical_scores = {}
    for record, document, length in zip(metadata, documents, lengths):
        score = 0.0
        for term in query_terms:
            frequency = document[term]
            if not frequency:
                continue
            df = document_frequency[term]
            idf = math.log(1 + (len(metadata) - df + 0.5) / (df + 0.5))
            denominator = frequency + 1.5 * (
                1 - 0.75 + 0.75 * length / average_length
            )
            score += idf * frequency * 2.5 / denominator
        lexical_scores[record["chunk_id"]] = score

    candidate_count = min(max(20, top_k), len(metadata))
    semantic = semantic_search(query, candidate_count)
    lexical = sorted(
        (record for record in metadata
         if lexical_scores[record["chunk_id"]] > 0),
        key=lambda record: (
            -lexical_scores[record["chunk_id"]], record["chunk_id"]
        ),
    )[:candidate_count]

    fused = Counter()
    for ranking in (semantic, lexical):
        for rank, record in enumerate(ranking, start=1):
            fused[record["chunk_id"]] += 1 / (60 + rank)

    records = {record["chunk_id"]: record for record in metadata}
    semantic_scores = {
        record["chunk_id"]: record["score"] for record in semantic
    }
    ordered_ids = sorted(fused, key=lambda cid: (-fused[cid], cid))
    results = []
    for cid in ordered_ids[:top_k]:
        record = records[cid].copy()
        record["hybrid_score"] = fused[cid]
        record["lexical_score"] = lexical_scores[cid]
        record["semantic_score"] = semantic_scores.get(cid)
        results.append(record)
    return results
