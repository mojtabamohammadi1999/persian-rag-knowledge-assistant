from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


def get_client(path="qdrant_storage"):
    return QdrantClient(path=path)


def index_chunks(client, collection, chunks, vectors):
    if client.collection_exists(collection):
        client.delete_collection(collection)

    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=vectors.shape[1], distance=Distance.COSINE),
    )

    points = [
        PointStruct(id=i, vector=vectors[i].tolist(), payload=chunks[i])
        for i in range(len(chunks))
    ]
    client.upsert(collection_name=collection, points=points)
    return client.count(collection_name=collection).count
