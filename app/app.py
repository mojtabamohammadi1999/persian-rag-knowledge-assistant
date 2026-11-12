import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gradio as gr

from src.generation.prompt import DOC_TITLES

ALL = "all"
CSS = "body, .gradio-container {direction: rtl;}"
EXAMPLES = [
    ["تدریس زبان عربی طبق قانون اساسی تا کدام مقطع تحصیلی الزامی است؟"],
    ["جلسه‌ی کمیته مرکزی انضباطی با حضور چند نفر رسمیت پیدا می‌کند؟"],
    ["انتقال اموال دولتی که جزو نفایس ملی است در چه صورتی ممکن است؟"],
    ["نمره‌ی ناتمام یک درس تا چند روز بعد از پایان امتحانات باید قطعی شود؟"],
    ["پایتخت فرانسه کجاست؟"],
]


def format_sources(out):
    if not out["sources"]:
        return ""
    lines = ["### منبع‌ها", ""]
    for s in out["sources"]:
        mark = "✅ " if s["index"] in out["cited"] else ""
        pages = f" | صفحه {s['pages']}" if s.get("pages") else ""
        lines.append(f"**{mark}[{s['index']}] {s['document']} - {s['label']}**{pages} | امتیاز {s['rerank_score']:.2f}")
        lines.append("> " + s["text"][:400].replace("\n", " ") + " ...")
        lines.append("")
    return "\n".join(lines)


def build_demo(pipeline):
    def respond(question, document):
        question = (question or "").strip()
        if not question:
            return "لطفاً یک سؤال بنویسید.", "", ""
        out = pipeline.ask(question, document=None if document == ALL else document)
        t = out["timings"]
        timing = (f"زمان: بازیابی {t['retrieval']:.2f} ثانیه | بازرتبه‌بندی {t['rerank']:.2f} ثانیه"
                  f" | تولید پاسخ {t['generation']:.1f} ثانیه")
        return out["answer"], format_sources(out), timing

    choices = [("همه‌ی اسناد", ALL)] + [(title, name) for name, title in DOC_TITLES.items()]
    with gr.Blocks(title="دستیار دانش (RAG)", css=CSS) as demo:
        gr.Markdown("# دستیار پرسش و پاسخ آیین‌نامه‌ها و قانون اساسی\n"
                    "پاسخ فقط از روی اسناد داده می‌شود و منبع‌ها زیر آن می‌آیند. "
                    "پاسخ‌ها ممکن است خطا داشته باشند؛ برای اطمینان به منبع‌ها مراجعه کنید.")
        with gr.Row():
            question = gr.Textbox(label="سؤال", lines=2, scale=4)
            document = gr.Dropdown(choices=choices, value=ALL, label="سند", scale=1)
        button = gr.Button("بپرس", variant="primary")
        gr.Markdown("### پاسخ")
        answer = gr.Markdown()
        sources = gr.Markdown()
        timing = gr.Markdown()
        gr.Examples(examples=EXAMPLES, inputs=question)
        button.click(respond, [question, document], [answer, sources, timing])
        question.submit(respond, [question, document], [answer, sources, timing])
    return demo


def main():
    parser = argparse.ArgumentParser(description="Gradio demo of the RAG assistant.")
    parser.add_argument("--share", action="store_true", help="create a public gradio.live link")
    args = parser.parse_args()

    from src.builder import build_pipeline
    demo = build_demo(build_pipeline())
    demo.queue().launch(share=args.share)


if __name__ == "__main__":
    main()
