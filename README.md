# UniTO Guide

Bachelor’s thesis project on the design and evaluation of a retrieval-augmented generation (RAG) assistant for prospective Computer Science students at the University of Turin.

The intended assistant will help students find and understand official information, provide verifiable source citations, and acknowledge when the available evidence is insufficient.

## Current status

The document ingestion and semantic retrieval baseline is implemented and has undergone an initial manually annotated evaluation.

LLM-based answer generation is not yet integrated.

## Current corpus

The source registry contains five official university pages covering:

- Course overview
- Enrolment procedures
- Admission requirements
- Teaching information
- Academic calendar

The sources are registered for the 2026/27 academic year, with a recorded review date of 20 August 2026.

## Implemented pipeline

1. Download active sources from the source registry.
2. Perform basic HTML validity checks.
3. Extract and clean textual content.
4. Split documents into chunks of approximately 1,600 characters.
5. Preserve source metadata and apply manual chunk exclusions.
6. Build normalized embeddings using `intfloat/multilingual-e5-small`.
7. Retrieve passages through vector similarity.
8. Annotate retrieved candidates and calculate evaluation metrics.

Embeddings run on CPU with `passage: ` and `query: ` prefixes. The index consists of NumPy arrays and JSONL metadata.

Command-line search displays retrieved passages and their source URLs. It returns three results by default; evaluation uses five.

## Preliminary retrieval results

The evaluation includes 10 questions and 50 manually annotated candidate passages.

| Metric | Result |
| --- | ---: |
| Hit Rate@1 | 0.80 |
| Hit Rate@3 | 0.90 |
| Hit Rate@5 | 1.00 |
| MRR@5 | 0.87 |

Hit Rate@k measures the proportion of questions with at least one relevant passage among the first k results.

The current evaluation scripts and saved files label this measure `recall_at_k`; the implemented calculation is Hit Rate rather than corpus-level Recall.

These results describe retrieval performance on a small preliminary dataset, not the quality of generated answers. The question about first-year courses retrieves its first relevant passage at rank five, identifying a concrete area for improvement.

## Repository structure

- `data/sources/`: source registry and metadata
- `data/evaluation/`: questions, annotated candidates, exclusions, and metrics
- `src/ingestion/`: downloading, validation, extraction, and chunking
- `src/retrieval/`: index construction and command-line search
- `src/evaluation/`: candidate generation, annotation, and metrics
- `tests/`: HTML extraction tests

## Dependencies and reproducibility

Dependencies are listed in `requirements.txt`. Python 3.10 or later is required by the current code.

Downloaded documents, processed text, chunks, and the embedding index are excluded from version control. A fresh checkout therefore does not include a ready-to-use index or the original corpus snapshot.

The five extraction tests require local copies of `S002.html` and `S003.html` in `data/raw/html/`.

Dependency versions are not yet pinned. Downloading the live sources again may produce different content and retrieval results.

## Known limitations

- Academic-year filtering is fixed to 2026–2027 and does not remove all historical content.
- Chunking can separate related table content or combine multiple topics.
- PDF downloading is supported, but PDF text extraction is not implemented.
- Evaluation is limited to 10 questions, without a separate held-out set or unanswerable questions.
- Regenerating retrieval candidates overwrites existing annotations.
- Answer generation, citation handling, and insufficient-evidence responses are not yet implemented.
- No user-facing interface is currently included.

## Next steps

- Preserve a reproducible corpus and retrieval baseline.
- Improve chunk structure and investigate retrieval errors.
- Integrate LLM-based answer generation with source citations.
- Evaluate answer correctness, grounding, and handling of insufficient evidence.
- Define the user interface and user evaluation protocol with the thesis supervisor.

## Disclaimer

UniTO Guide is an independent research prototype and is not an official University of Turin service.