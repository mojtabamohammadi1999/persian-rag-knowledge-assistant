"""Document loaders for PDF and HTML files."""
import re
import unicodedata
from pathlib import Path

import pymupdf
from bs4 import BeautifulSoup

from src.ingestion.text_cleaning import (
    break_before_inline_headings,
    clean_persian,
    fix_split_keywords,
    merge_lines,
    remove_diacritics,
)

TITLE = re.compile(r"^اصل\s")
CHAPTER = re.compile(r"^فصل\s")


def extract_page_text(page, top_cut=0, bottom_cut=9999):
    """Extract text of one PDF page, dropping blocks inside the header/footer zones."""
    kept = []
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, text, block_no, block_type = b
        if block_type != 0:
            continue
        if y1 <= top_cut or y0 >= bottom_cut:
            continue
        kept.append((y0, text))
    kept.sort()
    joined = "\n".join(t for _, t in kept)
    return unicodedata.normalize("NFKC", joined)


def process_pdf(path, top_cut=0, bottom_cut=9999):
    """Return one record per page: document name, page number, cleaned text."""
    doc = pymupdf.open(path)
    pages = []
    for i, page in enumerate(doc):
        text = extract_page_text(page, top_cut, bottom_cut)
        text = clean_persian(text)
        text = fix_split_keywords(text)
        text = break_before_inline_headings(text)
        text = merge_lines(text)
        pages.append({
            "document": Path(path).name,
            "page": i + 1,
            "text": text,
        })
    return pages


def drop_obsolete_blocks(lines):
    """Drop the old text of amended principles ('اصل سابق') and editorial-note blocks.

    A dropped block runs until the next principle title or chapter title.
    """
    kept = []
    skipping = False
    for i, l in enumerate(lines):
        is_old = l.strip().startswith("اصل سابق")
        is_note_title = (
            TITLE.match(l) is not None
            and i + 1 < len(lines)
            and lines[i + 1].startswith("به موجب اصلاحاتی")
        )
        if is_old or is_note_title:
            skipping = True
            continue
        if skipping and (TITLE.match(l) or CHAPTER.match(l)):
            skipping = False
        if not skipping:
            kept.append(l)
    return kept


def load_html_text(path):
    """Read a saved Wikisource HTML file and return the cleaned main text."""
    with open(path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    text = soup.select_one("#mw-content-text").get_text("\n", strip=True)

    text = unicodedata.normalize("NFKC", text)
    text = remove_diacritics(text)
    text = clean_persian(text)

    start = text.find("بسم الله")
    if start != -1:
        text = text[start:]
    end = text.rfind("\nمنابع\n")
    if end != -1:
        text = text[:end]

    text = "\n".join(drop_obsolete_blocks(text.split("\n")))
    return text
