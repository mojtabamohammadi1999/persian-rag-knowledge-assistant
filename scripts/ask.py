import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.builder import build_pipeline


def print_result(result, show_text=False):
    print("\nپاسخ:\n" + result["answer"])
    print("\nمنابع (* = ذکرشده در پاسخ):")
    for s in result["sources"]:
        mark = "*" if s["index"] in result["cited"] else " "
        pages = f" | صفحه {', '.join(str(p) for p in s['pages'])}" if s["pages"] else ""
        print(f" {mark}[{s['index']}] {s['document']} — {s['label']}{pages}"
              f" (rerank={s['rerank_score']:.3f})")
        if show_text:
            print("      " + s["text"][:300].replace("\n", " "))
    times = ", ".join(f"{k} {v:.1f}s" for k, v in result["timings"].items())
    print("\nزمان: " + times)


def main():
    parser = argparse.ArgumentParser(description="Ask the Persian RAG assistant a question.")
    parser.add_argument("question", nargs="?", help="Question text (omit for interactive mode)")
    parser.add_argument("--document", default=None, help="Restrict search to one document file name")
    parser.add_argument("--top-n", type=int, default=5, help="Chunks passed to the LLM")
    parser.add_argument("--show-text", action="store_true", help="Print a snippet of each source")
    args = parser.parse_args()

    rag = build_pipeline(top_n=args.top_n)

    if args.question:
        print_result(rag.ask(args.question, document=args.document), args.show_text)
        return

    print("حالت تعاملی. برای خروج یک سؤال خالی بفرست.")
    while True:
        question = input("\nسؤال: ").strip()
        if not question:
            break
        print_result(rag.ask(question, document=args.document), args.show_text)


if __name__ == "__main__":
    main()
