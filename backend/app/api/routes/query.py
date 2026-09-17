from fastapi import APIRouter, HTTPException

from app.schemas.query import HealthResponse, QueryRequest, QueryResponse
from app.services import generation, retrieval

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok" if retrieval.is_loaded() else "vector store not loaded",
        vector_store_loaded=retrieval.is_loaded(),
        num_chunks=retrieval.chunk_count(),
    )


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    if not retrieval.is_loaded():
        raise HTTPException(status_code=503, detail="Vector store is not loaded yet.")

    retrieved = retrieval.retrieve(request.question)
    if not retrieved:
        return QueryResponse(
            answer="I couldn't find relevant information in the law text for this question.",
            sources=[],
        )

    answer = generation.generate_answer(request.question, retrieved)
    sources = [f"Article {chunk['article']}" for chunk in retrieved]
    return QueryResponse(answer=answer, sources=sources)
