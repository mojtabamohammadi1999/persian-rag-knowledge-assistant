"""Baseline chunking: fixed-size windows with overlap, blind to document structure."""


def fixed_size_chunks(text, chunk_size=500, overlap=80):
    """Split text into windows of about chunk_size characters, never cutting inside a word."""
    chunks = []
    n = len(text)
    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            lower = start + chunk_size // 2
            cut = max(text.rfind(" ", lower, end), text.rfind("\n", lower, end))
            if cut != -1:
                end = cut
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= n:
            break
        new_start = max(end - overlap, start + 1)
        while 0 < new_start < n and not text[new_start - 1].isspace():
            new_start += 1
        start = new_start
    return chunks


def baseline_chunks(records, chunk_size=500, overlap=80):
    """Chunk every page record (or the whole HTML record) with fixed-size windows."""
    chunks = []
    for rec in records:
        pieces = fixed_size_chunks(rec["text"], chunk_size, overlap)
        for i, piece in enumerate(pieces):
            chunks.append({
                "document": rec["document"],
                "label": None,
                "chapter": None,
                "pages": [rec["page"]] if rec["page"] is not None else [],
                "part": i + 1,
                "n_parts": len(pieces),
                "text": piece,
            })
    return chunks
