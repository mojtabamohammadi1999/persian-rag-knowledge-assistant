"""Turn sections into final chunks (section-aware chunking)."""
import re

# split after sentence-ending punctuation followed by whitespace
SENTENCE_END = re.compile(r"(?<=[.؟!؛])\s+")


def group_pieces(pieces, max_chars, sep):
    """Group consecutive pieces into groups of at most max_chars characters."""
    groups = []
    current = ""
    for piece in pieces:
        candidate = piece if not current else current + sep + piece
        if current and len(candidate) > max_chars:
            groups.append(current)
            current = piece
        else:
            current = candidate
    if current:
        groups.append(current)
    return groups


def split_long_paragraph(paragraph, max_chars):
    """Split one very long paragraph at sentence boundaries."""
    sentences = SENTENCE_END.split(paragraph)
    return group_pieces(sentences, max_chars, sep=" ")


def chunk_section(section, max_chars=1000):
    """Return the chunks of one section. A short section stays one chunk."""
    text = section["text"]
    if len(text) <= max_chars:
        parts = [text]
    else:
        pieces = []
        for para in text.split("\n\n"):
            if len(para) > max_chars:
                pieces.extend(split_long_paragraph(para, max_chars))
            else:
                pieces.append(para)
        parts = group_pieces(pieces, max_chars, sep="\n\n")
        parts = [
            p if i == 0 else f"{section['label']} (ادامه)\n{p}"
            for i, p in enumerate(parts)
        ]

    return [
        {
            "document": section["document"],
            "label": section["label"],
            "chapter": section.get("chapter"),
            "pages": section["pages"],
            "part": i + 1,
            "n_parts": len(parts),
            "text": p,
        }
        for i, p in enumerate(parts)
    ]


def chunk_sections(sections, max_chars=1000):
    """Chunk a list of sections (each must carry its 'document' name)."""
    chunks = []
    for section in sections:
        chunks.extend(chunk_section(section, max_chars))
    return chunks
