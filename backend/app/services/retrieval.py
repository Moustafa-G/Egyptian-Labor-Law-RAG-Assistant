import logging

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)

_embedder: SentenceTransformer | None = None
_collection = None


def load_vector_store() -> None:
    """Load the embedder and the persisted Chroma collection once, at app startup."""
    global _embedder, _collection

    logger.info("Loading embedding model: %s", settings.embedding_model)
    _embedder = SentenceTransformer(settings.embedding_model)

    logger.info("Loading vector store from: %s", settings.vector_store_path.resolve())
    client = chromadb.PersistentClient(path=str(settings.vector_store_path))
    _collection = client.get_collection(name=settings.collection_name)

    logger.info("Vector store loaded with %d chunks", _collection.count())


def is_loaded() -> bool:
    return _embedder is not None and _collection is not None


def chunk_count() -> int:
    if _collection is None:
        return 0
    return _collection.count()


def retrieve(question: str, k: int | None = None) -> list[dict]:
    """Embed the question and return the top-k most relevant chunks."""
    if _embedder is None or _collection is None:
        raise RuntimeError("Vector store is not loaded yet. Call load_vector_store() at startup.")

    k = k or settings.top_k
    query_embedding = _embedder.encode([question]).tolist()
    results = _collection.query(query_embeddings=query_embedding, n_results=k)

    retrieved = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        retrieved.append(
            {
                "text": doc,
                "source": meta.get("source", "unknown"),
                "article": meta.get("article", "unknown"),
                "distance": dist,
            }
        )
    return retrieved
