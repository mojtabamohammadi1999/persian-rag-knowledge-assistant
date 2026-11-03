"""Persian text cleaning helpers."""
import re

# Invisible direction marks (LRM, RLM, embedding/override marks, BOM).
# The zero-width non-joiner (\u200c, Persian half-space) is NOT here on purpose.
INVISIBLE_MARKS = re.compile(r"[\u200e\u200f\u202a-\u202e\ufeff]")

# Letters used for lettered items: الف- ب- ج- د-
LETTER = r"(?:الف|ب|ج|د)"


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


def fix_split_keywords(text: str) -> str:
    """PDF extraction sometimes splits 'ماده' into 'ما ده'; repair it when a number follows."""
    return re.sub(r"ما\s+ده(?=\s*\d)", "ماده", text)


def break_before_inline_headings(text: str) -> str:
    """Start a new line before a 'ماده N -' heading that sits in the middle of a line."""
    return re.sub(r"[ \t]+(ماده\s*\d+\s*-)", r"\n\1", text)


def join_split_numbering(text: str) -> str:
    """Join item numbers that PDF extraction split into three lines ('2', '-', '3') into '2 - 3 '."""
    return re.sub(
        r"(?m)^[ \t]*(\d+)[ \t]*\n[ \t]*-[ \t]*\n[ \t]*(\d+)[ \t]*\n",
        r"\1 - \2 ",
        text,
    )


def split_lettered_items(text: str) -> str:
    """Start a new paragraph at lettered items ('الف-', 'ب-') and numbered sub-items ('1. ب-')."""
    # group items: after '.', ':' or ')' -- but not after a digit like '1.'
    text = re.sub(rf"(?<=[^\d][.:)])[ \t]+(?={LETTER}\s*-)", "\n\n", text)
    # numbered sub-items such as '1. ب-'
    text = re.sub(rf"[ \t]+(?=\d+\.\s*{LETTER}\s*-)", "\n\n", text)
    return text


def merge_lines(text: str) -> str:
    """Merge broken lines into paragraphs; new paragraph at ماده/تبصره/فصل/بند or '1 -'."""
    text = join_split_numbering(text)
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
    result = split_lettered_items(result)
    return result
