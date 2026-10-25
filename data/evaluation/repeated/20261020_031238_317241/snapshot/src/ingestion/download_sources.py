import csv
import time
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCES_FILE = PROJECT_ROOT / "data" / "sources" / "sources.csv"
HTML_DIRECTORY = PROJECT_ROOT / "data" / "raw" / "html"
PDF_DIRECTORY = PROJECT_ROOT / "data" / "raw" / "pdf"

REQUEST_HEADERS = {
    "User-Agent": "UniTO-Guide research prototype/0.1"
}


def load_active_sources():
    """Restituisce le fonti attive presenti nel file CSV."""

    with SOURCES_FILE.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            source
            for source in reader
            if source["status"].strip().lower() == "active"
        ]


def download_source(source):
    """Scarica una fonte e la salva come HTML o PDF."""

    source_id = source["source_id"]
    url = source["url"]

    response = requests.get(
        url,
        headers=REQUEST_HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()

    if "application/pdf" in content_type:
        destination = PDF_DIRECTORY / f"{source_id}.pdf"
    else:
        destination = HTML_DIRECTORY / f"{source_id}.html"

    destination.write_bytes(response.content)
    print(f"{source_id}: salvato in {destination.relative_to(PROJECT_ROOT)}")


def main():
    HTML_DIRECTORY.mkdir(parents=True, exist_ok=True)
    PDF_DIRECTORY.mkdir(parents=True, exist_ok=True)

    sources = load_active_sources()
    print(f"Fonti attive trovate: {len(sources)}\n")

    for source in sources:
        try:
            download_source(source)
        except requests.RequestException as error:
            print(f"{source['source_id']}: errore durante il download: {error}")

        # Evita di inviare troppe richieste ravvicinate al sito.
        time.sleep(1)


if __name__ == "__main__":
    main()
    