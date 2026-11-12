from src.chunking.build_chunks import add_header
from src.evaluation.retrieval_eval import evaluate_retrieval
from src.generation.pipeline import RAGPipeline
from src.generation.prompt import NO_ANSWER, SYSTEM_PROMPT, build_messages, prepare_for_llm
from src.ingestion.text_cleaning import fix_reversed_numbers

CHUNK = {"id": "sec-0001", "document": "constitution.html", "label": "اصل یکم", "pages": None,
         "text": "حکومت ایران جمهوری اسلامی است.", "score": 0.5, "rank": 1}


def test_fix_reversed_decimal_number():
    assert "2.5 سال" in fix_reversed_numbers("حداکثر 5/2 سال")


def test_fix_reversed_date():
    assert "91/5/8" in fix_reversed_numbers("مصوب 8/5/ 91")


def test_prepare_for_llm_separates_digits_and_letters():
    assert "سال 5" in prepare_for_llm("سال5")
    assert "5 سال" in prepare_for_llm("5سال")


def test_add_header_keeps_original_text():
    out = add_header(CHUNK)
    assert out["text"].endswith(CHUNK["text"])
    assert "اصل یکم" in out["text"].split("\n")[0]
    assert out["id"] == CHUNK["id"]


def test_build_messages_and_rules():
    messages = build_messages("سؤال آزمایشی؟", [CHUNK])
    assert [m["role"] for m in messages] == ["system", "user"]
    assert "سؤال آزمایشی؟" in messages[1]["content"]
    assert CHUNK["text"] in messages[1]["content"]
    assert NO_ANSWER in SYSTEM_PROMPT


def test_evaluate_retrieval_metrics():
    chunks = [{"text": "alpha beta"}, {"text": "gamma"}]
    eval_set = [{"id": "q1", "question": "?", "evidence": "gamma"}]
    report = evaluate_retrieval(lambda q, k: chunks[:k], chunks, eval_set, ks=(1, 3))
    row = report["per_question"][0]
    assert row["rank"] == 2 and row["hit@1"] == 0 and row["hit@3"] == 1
    assert report["summary"]["mrr"] == 0.5


class FakeRetriever:
    def search(self, question, k=10, document=None):
        return [dict(CHUNK)]


class FakeReranker:
    def rerank(self, question, candidates, top_n=None, **kwargs):
        return [{**c, "rerank_score": 0.9} for c in candidates][:top_n]


class FakeLLM:
    def __init__(self, answer):
        self.answer = answer

    def generate(self, messages, **kwargs):
        return self.answer


def test_pipeline_answer_with_citation():
    pipe = RAGPipeline(FakeRetriever(), FakeReranker(), FakeLLM("جمهوری اسلامی است [1]"))
    out = pipe.ask("حکومت ایران چیست؟")
    assert out["answered"] is True
    assert list(out["cited"]) == [1]
    assert out["sources"][0]["label"] == "اصل یکم"


def test_pipeline_no_answer():
    pipe = RAGPipeline(FakeRetriever(), FakeReranker(), FakeLLM(NO_ANSWER))
    out = pipe.ask("پایتخت فرانسه کجاست؟")
    assert out["answered"] is False
    assert list(out["cited"]) == []
