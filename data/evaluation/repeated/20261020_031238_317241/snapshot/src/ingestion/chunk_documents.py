import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCES_PATH = PROJECT_ROOT / "data" / "sources" / "sources.csv"
PROCESSED_DIRECTORY = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIRECTORY / "chunks.jsonl"

MAX_CHARS = 1600


def load_sources():
    """Carica i metadati delle fonti indicizzandoli per source_id."""
    with SOURCES_PATH.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return {row["source_id"]: row for row in reader}


def split_long_unit(text, max_chars):
    """Divide un paragrafo troppo lungo senza spezzare le parole."""
    words = text.split()
    parts = []
    current_words = []

    for word in words:
        candidate = " ".join(current_words + [word])

        if current_words and len(candidate) > max_chars:
            parts.append(" ".join(current_words))
            current_words = [word]
        else:
            current_words.append(word)

    if current_words:
        parts.append(" ".join(current_words))

    return parts


def create_chunks(text, max_chars=MAX_CHARS):
    """Crea chunk rispettando, quando possibile, i confini dei paragrafi."""
    units = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        units.extend(split_long_unit(line, max_chars))

    chunks = []
    current_units = []

    for unit in units:
        candidate = "\n".join(current_units + [unit])

        if current_units and len(candidate) > max_chars:
            chunks.append("\n".join(current_units))
            current_units = [unit]
        else:
            current_units.append(unit)

    if current_units:
        chunks.append("\n".join(current_units))

    return chunks


def read_document(file_path):
    """Restituisce il corpo testuale successivo all’intestazione."""
    document = file_path.read_text(encoding="utf-8")
    separator = "\n---\n\n"

    if separator not in document:
        raise ValueError(f"Separatore non trovato in {file_path.name}")

    return document.split(separator, maxsplit=1)[1].strip()


def main():
    sources = load_sources()
    records = []

    for file_path in sorted(PROCESSED_DIRECTORY.glob("S*.txt")):
        source_id = file_path.stem
        metadata = sources.get(source_id)

        if metadata is None:
            print(f"{source_id}: metadati non trovati, file ignorato")
            continue

        text = read_document(file_path)
        chunks = create_chunks(text)

        for index, chunk_text in enumerate(chunks, start=1):
            records.append(
                {
                    "chunk_id": f"{source_id}-C{index:03d}",
                    "source_id": source_id,
                    "title": metadata["title"],
                    "url": metadata["url"],
                    "authority": metadata["authority"],
                    "topic": metadata["topic"],
                    "academic_year": metadata["academic_year"],
                    "last_checked": metadata["last_checked"],
                    "text": chunk_text,
                    "char_count": len(chunk_text),
                }
            )

        print(f"{source_id}: creati {len(chunks)} chunk")

    with OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
        for record in records:
            output_file.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\nTotale: {len(records)} chunk salvati in {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
    