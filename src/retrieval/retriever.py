from qdrant_client.models import FieldCondition, Filter, MatchValue

from src.embeddings.embedder import embed_texts


class Retriever:
    def __init__(self, model, client, collection, query_prefix=""):
        self.model = model
        self.client = client
        self.collection = collection
        self.query_prefix = query_prefix

    def search(self, question, k=10, document=None):
        q_vec = embed_texts(self.model, [question], prefix=self.query_prefix)[0]

        query_filter = None
        if document is not None:
            query_filter = Filter(
                must=[FieldCondition(key="document", match=MatchValue(value=document))]
            )

        result = self.client.query_points(
            collection_name=self.collection,
            query=q_vec.tolist(),
            limit=k,
            query_filter=query_filter,
            with_payload=True,
        )
        return [
            {"rank": rank, "score": hit.score, **hit.payload}
            for rank, hit in enumerate(result.points, start=1)
        ]
