"""Persian text cleaning helpers."""
import re


def remove_diacritics(text: str) -> str:
    """Remove Arabic diacritics (harakat)."""
    return re.sub(r"[\u064B-\u0652\u0670]", "", text)


def clean_persian(text: str) -> str:
    """Remove kashida, convert Arabic yeh/kaf to Persian, collapse spaces."""
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
