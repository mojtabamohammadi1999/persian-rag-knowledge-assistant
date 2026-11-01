"""Split documents into sections (articles / principles) while keeping metadata."""
import re

# 'ماده 5 -' (disciplinary regulation) or 'ماده5.' (education regulation)
ARTICLE_HEADING = re.compile(r"^ماده\s*(\d+)\s*[.\-]")

# Constitution: one line per heading
PRINCIPLE_TITLE = re.compile(r"^اصل\s")
CHAPTER_TITLE = re.compile(r"^فصل\s")


def split_into_articles(page_records):
    """Split the page records of ONE document into articles.

    A paragraph starts a new article only if it looks like an article heading
    AND its number is exactly the expected next number (1, 2, 3, ...).
    Everything before article 1 is kept as a 'مقدمه' section.
    """
    sections = [{"label": "مقدمه", "pages": [], "text": ""}]
    expected = 1

    for rec in page_records:
        for para in rec["text"].split("\n\n"):
            if not para.strip():
                continue
            m = ARTICLE_HEADING.match(para)
            if m and int(m.group(1)) == expected:
                sections.append({"label": f"ماده {expected}", "pages": [], "text": ""})
                expected += 1
            section = sections[-1]
            section["text"] += ("\n\n" if section["text"] else "") + para
            if rec["page"] not in section["pages"]:
                section["pages"].append(rec["page"])

    return [s for s in sections if s["text"]]


def split_into_principles(text):
    """Split the constitution text into principles; remember the current chapter.

    Everything before the first principle is kept as a 'مقدمه' section.
    The chapter title is stored as metadata, not inside the principle text.
    """
    sections = [{"label": "مقدمه", "chapter": None, "pages": [], "text": ""}]
    chapter = None

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if CHAPTER_TITLE.match(line):
            chapter = line
            continue
        if PRINCIPLE_TITLE.match(line):
            sections.append({"label": line, "chapter": chapter, "pages": [], "text": line})
            continue
        section = sections[-1]
        section["text"] += ("\n\n" if section["text"] else "") + line

    return [s for s in sections if s["text"]]
