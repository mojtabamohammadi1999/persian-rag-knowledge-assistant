import json
import os

import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")


def load_embedder(model_name=DEFAULT_MODEL, device="cuda", half=True):
    model = SentenceTransformer(model_name, device=device)
    if half and device == "cuda":
        model.half()
    return model


def embed_texts(model, texts, batch_size=16, prefix=""):
    # texts باید فهرستی از رشته‌ها باشد (نه یک رشته‌ی تکی)
    vectors = model.encode(
        [prefix + t for t in texts],
        batch_size=batch_size,
        normalize_embeddings=True,
    )
    return vectors.astype("float32")


def embed_chunks_file(model, chunks_path, vectors_path):
    with open(chunks_path, encoding="utf-8") as f:
        chunks = json.load(f)
    vectors = embed_texts(model, [c["text"] for c in chunks])
    np.save(vectors_path, vectors)
    return chunks, vectors
