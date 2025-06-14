from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.core.models.chunks import Chunks
from app.core.services.chunks import ChunksService
from app.infrastructure.locking import LockManager
from app.infrastructure.persistence import Persistence

router = APIRouter()


def get_chunk_service(
    db: Persistence = Depends(Persistence),
    lock_manager: LockManager = Depends(LockManager),
) -> ChunksService:
    return ChunksService(db, lock_manager)


@router.post(
    "/chunks",
    response_model=Chunks,
    status_code=status.HTTP_201_CREATED,
    summary="Add chunk to document",
)
async def create_chunk(
    library_id: UUID,
    document_id: UUID,
    text: str = Body(...),
    embedding: List[float] = Body(...),
    metadata: Optional[Dict[str, str]] = Body(None),
    service: ChunksService = Depends(get_chunk_service),
):
    chunk = service.add_chunk(
        library_id,
        document_id,
        text,
        embedding,
        metadata,
    )
    if not chunk:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Library or Document not found")
    return chunk


@router.get("/chunks", response_model=List[Chunks], summary="List chunks")
async def list_chunks(
    library_id: UUID,
    document_id: UUID,
    service: ChunksService = Depends(get_chunk_service),
):
    chunks = service.list_chunks(library_id, document_id)
    if chunks is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Library or Document not found")
    return chunks


@router.get("/chunks/{chunk_id}", response_model=Chunks, summary="Get chunk details")
async def get_chunk(
    library_id: UUID,
    document_id: UUID,
    chunk_id: UUID,
    service: ChunksService = Depends(get_chunk_service),
):
    chunk = service.get_chunk(library_id, document_id, chunk_id)
    if not chunk:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chunk not found")
    return chunk


@router.put("/chunks/{chunk_id}", response_model=Chunks, summary="Update chunk")
async def update_chunk(
    library_id: UUID,
    document_id: UUID,
    chunk_id: UUID,
    text: Optional[str] = Body(None),
    embedding: Optional[List[float]] = Body(None),
    metadata: Optional[Dict[str, str]] = Body(None),
    service: ChunksService = Depends(get_chunk_service),
):
    chunk = service.update_chunk(library_id, document_id, chunk_id, text, embedding, metadata)
    if not chunk:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chunk not found")
    return chunk


@router.delete("/chunks/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete chunk")
async def delete_chunk(
    library_id: UUID,
    document_id: UUID,
    chunk_id: UUID,
    service: ChunksService = Depends(get_chunk_service),
):
    if not service.delete_chunk(library_id, document_id, chunk_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chunk not found")


@router.post(
    "/chunks/search",
    summary="Search chunks",
    description="Performs k-NN search on chunks in the document",
)
async def search_chunks(
    library_id: UUID,
    document_id: UUID,
    embedding: List[float] = Body(...),
    k: int = Body(5),
    filters: Optional[Dict] = Body(None),
    service: ChunksService = Depends(get_chunk_service),
):
    results = service.search_chunks(library_id, embedding, k, filters)
    if results is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Library not found, not indexed, or no chunks available",
        )
    return [{"chunk": chunk.dict(), "similarity": score} for chunk, score in results]
