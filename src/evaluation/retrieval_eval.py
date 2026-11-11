import json
from pathlib import Path


def summarize(rows, ks):
    n = len(rows)
    covered = [r for r in rows if r["n_relevant"] > 0]
    summary = {
        "n_questions": n,
        "coverage": len(covered) / n,
        "mrr": sum(1 / r["rank"] for r in rows if r["rank"]) / n,
    }
    for k in ks:
        summary[f"hit@{k}"] = sum(r[f"hit@{k}"] for r in rows) / n
        summary[f"precision@{k}"] = sum(r[f"precision@{k}"] for r in rows) / n
        summary[f"recall@{k}"] = (
            sum(r[f"recall@{k}"] for r in covered) / len(covered) if covered else 0.0
        )
    return summary


def evaluate_retrieval(search_fn, chunks, eval_set, ks=(1, 3, 5, 10)):
    max_k = max(ks)
    rows = []
    for item in eval_set:
        evidence = item["evidence"]
        n_relevant = sum(1 for c in chunks if evidence in c["text"])
        results = search_fn(item["question"], max_k)
        flags = [evidence in r["text"] for r in results]
        rank = next((i for i, hit in enumerate(flags, start=1) if hit), None)

        row = {"id": item["id"], "n_relevant": n_relevant, "rank": rank}
        for k in ks:
            found = sum(flags[:k])
            row[f"hit@{k}"] = int(found > 0)
            row[f"precision@{k}"] = found / k
            row[f"recall@{k}"] = found / n_relevant if n_relevant else None
        rows.append(row)
    return {"summary": summarize(rows, ks), "per_question": rows}


def save_report(report, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
