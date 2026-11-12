"""Build the whole index from raw documents:
documents -> chunks -> chunks with headers -> embeddings -> Qdrant."""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    parser = argparse.ArgumentParser(description="Build the RAG index from raw documents.")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--qdrant-path", default="qdrant_storage")
    parser.add_argument("--all", action="store_true",
                        help="also index the plain section and fixed-size collections (for experiments)")
    args = parser.parse_args()

    from src.chunking.build_chunks import add_header, build_and_save_chunks
    from src.embeddings.embedder import embed_texts, load_embedder
    from src.ingestion.build_documents import build_documents
    from src.retrieval.vector_store import get_client, index_chunks

    processed = Path(args.processed_dir)
    records = build_documents(args.raw_dir, processed / "documents.json")
    print(len(records), "records from raw documents")

    outputs = build_and_save_chunks(args.processed_dir)
    titled = [add_header(c) for c in outputs["chunks_section.json"]]
    with open(processed / "chunks_titled.json", "w", encoding="utf-8") as f:
        json.dump(titled, f, ensure_ascii=False, indent=2)

    targets = {"chunks_titled": titled}
    if args.all:
        targets["chunks_section"] = outputs["chunks_section.json"]
        targets["chunks_fixed"] = outputs["chunks_fixed.json"]

    model = load_embedder()
    client = get_client(args.qdrant_path)
    for name, chunks in targets.items():
        vectors = embed_texts(model, [c["text"] for c in chunks])
        np.save(processed / f"emb_{name.split('_')[1]}.npy", vectors)
        count = index_chunks(client, name, chunks, vectors)
        print(name, "<-", count, "points")


if __name__ == "__main__":
    main()
