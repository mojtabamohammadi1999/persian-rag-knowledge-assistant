from src.embeddings.embedder import load_embedder
from src.generation.llm import LocalLLM
from src.generation.pipeline import RAGPipeline
from src.reranking.reranker import Reranker
from src.retrieval.retriever import Retriever
from src.retrieval.vector_store import get_client


def build_pipeline(collection="chunks_section", qdrant_path="qdrant_storage",
                   candidates_k=20, top_n=5):
    embedder = load_embedder()
    client = get_client(qdrant_path)
    retriever = Retriever(embedder, client, collection)
    reranker = Reranker()
    llm = LocalLLM()
    return RAGPipeline(retriever, reranker, llm, candidates_k=candidates_k, top_n=top_n)
