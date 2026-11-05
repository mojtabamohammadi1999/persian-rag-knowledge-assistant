import json

import numpy as np


def load_eval_set(path="data/eval/eval_questions.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def first_relevant_rank(texts, evidence):
    for rank, text in enumerate(texts, start=1):
        if evidence in text:
            return rank
    return None


def eval_matrix(vectors, chunks, q_vecs, eval_set, k=10):
    ranks = []
    for item, q in zip(eval_set, q_vecs):
        order = np.argsort(-(vectors @ q))[:k]
        texts = [chunks[idx]["text"] for idx in order]
        ranks.append(first_relevant_rank(texts, item["evidence"]))
    return ranks


def summarize_ranks(ranks):
    n = len(ranks)
    return {
        "hit@1": sum(1 for r in ranks if r is not None and r <= 1) / n,
        "hit@3": sum(1 for r in ranks if r is not None and r <= 3) / n,
        "mrr": sum(1 / r for r in ranks if r is not None) / n,
    }
