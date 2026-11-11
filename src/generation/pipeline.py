import re
import time

from src.generation.prompt import DOC_TITLES, NO_ANSWER, build_messages


class RAGPipeline:
    def __init__(self, retriever, reranker, llm, candidates_k=20, top_n=4):
        self.retriever = retriever
        self.reranker = reranker
        self.llm = llm
        self.candidates_k = candidates_k
        self.top_n = top_n

    def ask(self, question, document=None):
        t0 = time.perf_counter()
        candidates = self.retriever.search(question, k=self.candidates_k, document=document)
        t1 = time.perf_counter()
        top_chunks = self.reranker.rerank(question, candidates, top_n=self.top_n)
        t2 = time.perf_counter()
        answer = self.llm.generate(build_messages(question, top_chunks))
        t3 = time.perf_counter()

        numbers = {int(n) for n in re.findall(r"\[(\d+)\]", answer)}
        cited = sorted(n for n in numbers if 1 <= n <= len(top_chunks))

        sources = [
            {
                "index": i,
                "document": DOC_TITLES.get(c["document"], c["document"]),
                "label": c.get("label"),
                "pages": c.get("pages", []),
                "rerank_score": c["rerank_score"],
                "text": c["text"],
            }
            for i, c in enumerate(top_chunks, start=1)
        ]
        return {
            "question": question,
            "answer": answer,
            "answered": NO_ANSWER not in answer,
            "cited": cited,
            "sources": sources,
            "timings": {
                "retrieval": t1 - t0,
                "rerank": t2 - t1,
                "generation": t3 - t2,
            },
        }
