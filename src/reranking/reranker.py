import os

from sentence_transformers import CrossEncoder

DEFAULT_RERANKER = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")


class Reranker:
    def __init__(self, model_name=DEFAULT_RERANKER, device="cuda", max_length=1024, half=True):
        self.model = CrossEncoder(model_name, device=device, max_length=max_length)
        if half and device == "cuda":
            self.model.model.half()

    def rerank(self, question, candidates, top_n=None, batch_size=8):
        if not candidates:
            return []
        scores = self.model.predict(
            [(question, c["text"]) for c in candidates], batch_size=batch_size
        )
        scored = [{**c, "rerank_score": float(s)} for c, s in zip(candidates, scores)]
        scored.sort(key=lambda c: c["rerank_score"], reverse=True)
        return scored[:top_n]
