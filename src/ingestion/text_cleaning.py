"""Persian text cleaning helpers."""
import re

# Invisible direction marks (LRM, RLM, embedding/override marks, BOM).
# The zero-width non-joiner (\u200c, Persian half-space) is NOT here on purpose.
INVISIBLE_MARKS = re.compile(r"[\u200e\u200f\u202a-\u202e\ufeff]")


def remove_diacritics(text: str) -> str:
    """Remove Arabic diacritics (harakat)."""
    return re.sub(r"[\u064B-\u0652\u0670]", "", text)


def clean_persian(text: str) -> str:
    """Remove invisible marks and kashida, convert Arabic yeh/kaf to Persian, collapse spaces."""
    text = INVISIBLE_MARKS.sub("", text)
    text = text.replace("\u0640", "")
    text = text.replace("\u064a", "\u06cc")
    text = text.replace("\u0643", "\u06a9")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def merge_lines(text: str) -> str:
    """Merge broken lines into paragraphs; new paragraph at ماده/تبصره/فصل/بند or '1 -'."""
    new_para = re.compile(r"^(ماده|تبصره|فصل|بند)\s*\d+|^\d+\s*-")
    paragraphs = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if not paragraphs or new_para.match(line):
            paragraphs.append(line)
        else:
            paragraphs[-1] += " " + line
    result = "\n\n".join(paragraphs)
    result = re.sub(r"\s+([:.،؛])", r"\1", result)
    return result
