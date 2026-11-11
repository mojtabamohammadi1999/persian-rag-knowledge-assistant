NO_ANSWER = "اطلاعات کافی برای پاسخ به این سؤال در اسناد موجود نیست."

DOC_TITLES = {
    "discipline_regulation.pdf": "آیین‌نامه انضباطی دانشجویان",
    "education_regulation.pdf": "آیین‌نامه آموزشی دوره کارشناسی",
    "constitution.html": "قانون اساسی جمهوری اسلامی ایران",
}

SYSTEM_PROMPT = f"""شما دستیار پاسخ‌گویی به سؤال‌های مربوط به قوانین و آیین‌نامه‌ها هستید.
قواعد پاسخ‌گویی:
1. فقط بر اساس «متن‌های مرجع» داده‌شده پاسخ بده. از دانسته‌های خودت یا حدس استفاده نکن.
2. پاسخ را به فارسی، کوتاه و دقیق بنویس.
3. بعد از هر ادعا شماره‌ی منبع را به شکل [1] یا [2] بنویس.
4. اگر پاسخ در متن‌های مرجع نیست، فقط همین جمله را بنویس: «{NO_ANSWER}»"""


def format_source(index, chunk):
    parts = [DOC_TITLES.get(chunk["document"], chunk["document"])]
    if chunk.get("label"):
        parts.append(chunk["label"])
    if chunk.get("pages"):
        parts.append("صفحه " + "، ".join(str(p) for p in chunk["pages"]))
    return f"[{index}] " + " — ".join(parts)


def build_messages(question, chunks):
    blocks = [
        f"{format_source(i, c)}\n{c['text']}"
        for i, c in enumerate(chunks, start=1)
    ]
    context = "\n\n".join(blocks)
    user_content = f"متن‌های مرجع:\n\n{context}\n\nسؤال: {question}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
