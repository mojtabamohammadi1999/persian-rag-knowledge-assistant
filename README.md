# Persian RAG Knowledge Assistant

Question answering over Iranian university regulations and the Constitution, in Persian.
A local LLM answers **only** from retrieved passages and cites its sources.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mojtabamohammadi1999/production-rag-knowledge-assistant/blob/main/notebooks/demo_colab.ipynb)

**Try it:** click the Colab badge, select a T4 GPU, and run the three cells. The first run takes about
15 minutes (a ~15 GB model download). The last cell prints a public Gradio link and keeps running while the demo is alive;
stop the cell to shut the demo down.

## What it does

- Documents: student discipline regulation (PDF), undergraduate education regulation (PDF), Constitution of the Islamic Republic of Iran (HTML).
- Answers in Persian with citations like `[1]`, and shows the source passages (document, article, page, reranker score).
- Says "not enough information in the documents" when the answer is not in the sources.
- Everything runs locally on one free Colab T4 GPU. No external API is used.

## Architecture

~~~text
PDF / HTML
  -> cleaning (Persian normalisation, reversed-number fix)
  -> section-aware chunking (one article per chunk, split if > 1000 chars) + header "document | chapter | article"
  -> BGE-M3 embeddings (1024-d, cosine)  -> Qdrant (local mode)

question -> embed -> top 20 from Qdrant -> bge-reranker-v2-m3 -> top 5
         -> prompt with numbered sources -> Qwen2.5-7B-Instruct (4-bit) -> answer + citations
~~~

| Component | Choice |
|---|---|
| Embeddings | `BAAI/bge-m3` (fp16) |
| Vector store | Qdrant, local mode |
| Reranker | `BAAI/bge-reranker-v2-m3` (cross-encoder) |
| LLM | `Qwen/Qwen2.5-7B-Instruct`, 4-bit NF4 (bitsandbytes), greedy decoding |
| UI | Gradio |

## Evaluation

Retrieval was measured on two sets built from the documents: an **easy set** (36 questions, written from the chunks, so
optimistic) and a **hard set** (35 paraphrased questions that avoid the keywords of the text). A passage counts as relevant
if it contains a fixed evidence string, so different chunking methods can be compared fairly.

| Configuration | Easy Hit@1 | Easy MRR | Hard Hit@1 | Hard Hit@3 | Hard MRR |
|---|---|---|---|---|---|
| Fixed-size chunks (500/80), no reranker | 0.833 | 0.880 | 0.714 | 0.886 | 0.806 |
| Fixed-size chunks, reranker | 0.917 | 0.949 | 0.829 | 0.914 | 0.880 |
| Section-aware chunks, no reranker | 0.889 | 0.925 | 0.857 | 0.943 | 0.909 |
| Section-aware chunks, reranker | 1.000 | 1.000 | 0.857 | 0.971 | 0.914 |
| Section-aware + header, no reranker | 0.972 | 0.986 | 0.857 | 0.971 | 0.920 |
| **Section-aware + header + reranker (default)** | 1.000 | 1.000 | 0.857 | 0.971 | 0.917 |

What the numbers say:
- Section-aware chunking beats fixed-size chunking in every comparison, but the sets are small (one question is about 0.03).
- The reranker helps fixed-size chunks a lot and section-aware chunks little; on the easy set it reaches the ceiling.
- Adding the article title to each chunk gives a small, never negative gain.
- Only the top 5 passages reach the LLM, so Hit@3 to Hit@5 matters more than Hit@1.

**Answer quality** was checked by hand on 12 questions (see `results/generation_samples.json`): of 9 questions about the
documents, 4 were correct, 2 partially correct and 3 wrong; all 3 off-topic or unanswerable questions were correctly refused.
This is a small, manual check, not a benchmark.

Latency on a T4: retrieval ~0.04 s, reranking 0.2-0.4 s, generation 3-30 s depending on answer length.

## Limitations (honest list)

- The 7B model sometimes ignores evidence it was given (for example it listed only one of several restrictions) or answers a neighbouring question.
- Multi-hop questions fail: when a violation is defined in one article and its penalty in another, the model cannot connect them (cheating-penalty example in `docs/findings.md`).
- The reranker can push a correct passage down when the question uses different words from the text (hijab vs "Islamic dress"; the passage fell from rank 10 to 17 and was never shown to the LLM). A score threshold for refusing would therefore reject valid questions, so refusal relies on the prompt only.
- Questions about the structure of a document ("how many articles?") cannot be answered by retrieval.
- Text extraction from the PDFs reverses some digits and the preface of one PDF; a number fix and a prompt-time cleanup handle the common cases, not all.
- Evaluation sets are small and partly written from the chunks; the generation check is manual and small.
- Three documents, Persian only, no conversation memory, and no API or container packaging (FastAPI and Docker were left out on purpose for this project).

More details and the experiment log: [`docs/findings.md`](docs/findings.md).

## Run it yourself

Requires a CUDA GPU (a free Colab T4 is enough).

~~~bash
git clone https://github.com/mojtabamohammadi1999/production-rag-knowledge-assistant.git
cd production-rag-knowledge-assistant
pip install -r requirements.txt

python scripts/build_index.py                 # raw documents -> chunks -> embeddings -> Qdrant
python scripts/ask.py "your question" --show-text   # command line
python app/app.py --share                     # Gradio demo
python -m pytest -q                           # unit tests (no GPU needed)
~~~

Models can be changed with the environment variables `EMBEDDING_MODEL`, `RERANKER_MODEL` and `LLM_MODEL`.
`python scripts/build_index.py --all` also builds the plain section and fixed-size collections used in the experiments.

## Repository layout

~~~text
app/            Gradio demo
scripts/        build_index.py, ask.py (CLI)
src/
  ingestion/    PDF/HTML loading and Persian text cleaning
  chunking/     section-aware and fixed-size chunking, chunk headers
  embeddings/   BGE-M3 embedding
  retrieval/    Qdrant store and retriever
  reranking/    cross-encoder reranker
  generation/   prompt, local LLM, pipeline
  evaluation/   metrics and retrieval evaluation
data/raw/       the three source documents (see data/README.md)
data/eval/      evaluation questions (easy and hard sets)
results/        evaluation outputs (JSON)
docs/           experiment log (findings.md)
tests/          unit tests
notebooks/      clean Colab demo notebook
~~~

## خلاصه‌ی فارسی

دستیار پرسش و پاسخ فارسی برای آیین‌نامه‌ی انضباطی دانشجویان، آیین‌نامه‌ی آموزشی کارشناسی و قانون اساسی.
سیستم با embedding چندزبانه‌ی BGE-M3 و Qdrant متن‌های مرتبط را پیدا می‌کند، با reranker مرتب می‌کند و یک مدل زبانی محلی
(Qwen2.5-7B، ۴ بیتی) فقط از روی همین متن‌ها پاسخ می‌دهد و منبع را نشان می‌دهد. دمو را با دکمه‌ی Colab در بالا می‌توان اجرا کرد.
