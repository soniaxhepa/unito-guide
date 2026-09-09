from pathlib import Path

from src.ingestion.extract_html import extract_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
S003_PATH = PROJECT_ROOT / "data" / "raw" / "html" / "S003.html"
S002_PATH = PROJECT_ROOT / "data" / "raw" / "html" / "S002.html"

def test_s003_preserves_current_academic_year():
    _, text = extract_text(S003_PATH)

    assert "2026-2027" in text
    assert "TOLC-S" in text
    assert "Obblighi Formativi Aggiuntivi" in text

def test_s003_removes_previous_academic_years():
    _, text = extract_text(S003_PATH)

    assert "2025-2026" not in text
    assert "2024-2025" not in text
    assert "2023-2024" not in text

def test_s003_removes_interface_icons():
    _, text = extract_text(S003_PATH)

    assert "keyboard_arrow_down" not in text


def test_s002_contains_current_enrolment_information():
    _, text = extract_text(S002_PATH)

    assert "Anno Accademico 2026-2027" in text
    assert "19 ottobre 2026" in text
    assert "21 ottobre 2026" in text
    assert "TARM" in text

def test_s002_removes_previous_academic_year():
    _, text = extract_text(S002_PATH)

    assert "2025-2026" not in text
    assert "2024-2025" not in text
