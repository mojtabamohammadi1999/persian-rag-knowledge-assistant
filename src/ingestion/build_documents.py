"""Build data/processed/documents.json from the files in data/raw."""
import json
from pathlib import Path

from src.ingestion.loaders import process_pdf, load_html_text

# Header/footer cut zones per PDF (y position in points, measured from the top of the page)
PDF_CONFIG = {
    "discipline_regulation.pdf": {"top_cut": 148, "bottom_cut": 770},
    "education_regulation.pdf": {"top_cut": 0, "bottom_cut": 9999},
}
HTML_FILES = ["constitution.html"]


def build_documents(raw_dir, out_path):
    raw_dir = Path(raw_dir)
    records = []

    for name, cfg in PDF_CONFIG.items():
        records += process_pdf(raw_dir / name, **cfg)

    for name in HTML_FILES:
        records.append({
            "document": name,
            "page": None,
            "text": load_html_text(raw_dir / name),
        })

    for r in records:
        r["doc_type"] = Path(r["document"]).suffix.lstrip(".")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return records
