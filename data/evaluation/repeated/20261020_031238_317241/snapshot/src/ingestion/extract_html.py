import re
from pathlib import Path

from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HTML_DIRECTORY = PROJECT_ROOT / "data" / "raw" / "html"
PROCESSED_DIRECTORY = PROJECT_ROOT / "data" / "processed"

UNWANTED_TAGS = [
    "script",
    "style",
    "nav",
    "footer",
    "header",
    "aside",
    "form",
    "noscript",
    "svg",
]

UI_ONLY_LINES = {
    "italiano English",
    "Apply for a Bachelor Course at the University of Torino",
}


def normalize_line(text):
    """Normalizza spazi e caratteri invisibili senza modificare il contenuto."""
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def extract_text(file_path):
    """Estrae blocchi testuali coerenti dal contenuto principale."""

    html = file_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text(" ", strip=True) if soup.title else ""

    main_content = soup.find("main") or soup.find("article") or soup.body or soup

    current_academic_year = "2026-2027"

    # Elimina soltanto gli accordion appartenenti ad annualità precedenti.
    for button in main_content.select('[data-bs-toggle="collapse"]'):
        heading_text = normalize_line(button.get_text(" ", strip=True))
        normalized_heading = (
            heading_text.replace("–", "-")
            .replace("—", "-")
            .replace(" ", "")
        )

        academic_years = re.findall(
            r"20\d{2}-20\d{2}",
            normalized_heading,
        )

        if academic_years and current_academic_year not in academic_years:
            target_id = button.get("aria-controls")

            if target_id:
                target_content = main_content.find(id=target_id)
                if target_content:
                    target_content.decompose()

            heading = button.find_parent(["h1", "h2", "h3", "h4"])

            if heading:
                heading.decompose()
            else:
                button.decompose()

    # Elimina le icone Material trasformate erroneamente in testo.
    for icon in main_content.select("i.material-icons"):
        icon.decompose()

    for tag_name in UNWANTED_TAGS:
        for element in main_content.find_all(tag_name):
            element.decompose()

    content_tags = ["h1", "h2", "h3", "h4", "p", "li", "th", "td"]

    clean_lines = []
    previous_line = None

    for element in main_content.find_all(content_tags):
        # Evita di estrarre due volte elementi annidati,
        # per esempio un paragrafo contenuto in un elemento di lista.
        if element.find_parent(content_tags):
            continue

        line = normalize_line(element.get_text(" ", strip=True))

        if line in UI_ONLY_LINES:
            continue

        # Elimina le etichette isolate che rimandano ad anni accademici passati.
        isolated_academic_year = re.fullmatch(r"20\d{2}/20\d{2}", line)

        if isolated_academic_year:
            normalized_year = line.replace("/", "-")

            if normalized_year != current_academic_year:
                continue

        if not line:
            continue

        if line == previous_line:
            continue

        clean_lines.append(line)
        previous_line = line

    return title, "\n".join(clean_lines)


def main():
    PROCESSED_DIRECTORY.mkdir(parents=True, exist_ok=True)

    html_files = sorted(HTML_DIRECTORY.glob("*.html"))

    for file_path in html_files:
        source_id = file_path.stem
        title, text = extract_text(file_path)

        output_path = PROCESSED_DIRECTORY / f"{source_id}.txt"

        document = (
            f"SOURCE_ID: {source_id}\n"
            f"TITLE: {title}\n"
            f"FILE_TYPE: html\n"
            f"\n---\n\n"
            f"{text}\n"
        )

        output_path.write_text(document, encoding="utf-8")

        print(
            f"{source_id}: estratti {len(text)} caratteri "
            f"in {output_path.relative_to(PROJECT_ROOT)}"
        )


if __name__ == "__main__":
    main()



