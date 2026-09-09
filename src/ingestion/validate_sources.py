from pathlib import Path

from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HTML_DIRECTORY = PROJECT_ROOT / "data" / "raw" / "html"

ERROR_MESSAGES = [
    "accesso negato",
    "pagina non trovata",
    "not found",
    "forbidden",
]

MINIMUM_TEXT_LENGTH = 500


def validate_html(file_path):
    """Controlla che un file HTML contenga una pagina plausibilmente valida."""

    html = file_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text(" ", strip=True) if soup.title else "Titolo assente"
    text = soup.get_text(" ", strip=True)
    normalized_text = text.lower()

    detected_errors = [
        message
        for message in ERROR_MESSAGES
        if message in normalized_text
    ]

    is_valid = (
        len(text) >= MINIMUM_TEXT_LENGTH
        and not detected_errors
    )

    return {
        "file": file_path.name,
        "title": title,
        "text_length": len(text),
        "errors": detected_errors,
        "is_valid": is_valid,
    }


def main():
    html_files = sorted(HTML_DIRECTORY.glob("*.html"))

    if not html_files:
        print("Nessun file HTML trovato.")
        return

    for file_path in html_files:
        result = validate_html(file_path)
        status = "VALIDA" if result["is_valid"] else "DA CONTROLLARE"

        print(f"\n{result['file']} — {status}")
        print(f"Titolo: {result['title']}")
        print(f"Caratteri di testo: {result['text_length']}")

        if result["errors"]:
            print(f"Possibili errori: {', '.join(result['errors'])}")


if __name__ == "__main__":
    main()
    