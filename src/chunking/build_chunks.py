import json
from pathlib import Path

from src.chunking.chunker import chunk_sections
from src.chunking.fixed import baseline_chunks
from src.chunking.sections import split_into_articles, split_into_principles

PDF_DOCS = ["discipline_regulation.pdf", "education_regulation.pdf"]
HTML_DOC = "constitution.html"


def build_all_sections(records):
    sections = []
    for name in PDF_DOCS:
        doc_records = [r for r in records if r["document"] == name]
        for section in split_into_articles(doc_records):
            section["document"] = name
            sections.append(section)
    constitution = [r for r in records if r["document"] == HTML_DOC][0]
    for section in split_into_principles(constitution["text"]):
        section["document"] = HTML_DOC
        sections.append(section)
    return sections


def assign_ids(chunks, prefix):
    for i, chunk in enumerate(chunks, start=1):
        chunk["id"] = f"{prefix}-{i:04d}"
    return chunks


def build_and_save_chunks(processed_dir="data/processed"):
    processed = Path(processed_dir)
    with open(processed / "documents.json", encoding="utf-8") as f:
        records = json.load(f)

    outputs = {
        "chunks_section.json": assign_ids(
            chunk_sections(build_all_sections(records), max_chars=1000), "sec"),
        "chunks_fixed.json": assign_ids(
            baseline_chunks(records, chunk_size=500, overlap=80), "fix"),
    }
    for name, chunks in outputs.items():
        with open(processed / name, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        print(name, "←", len(chunks), "chunk")
    return outputs
