from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.models.documents import DocumentCreate, Documents, DocumentUpdate
from app.core.services.documents import DocumentsService
from app.infrastructure.locking import LockManager
from app.infrastructure.persistence import Persistence

router = APIRouter(prefix="/libraries/{library_id}/documents", tags=["documents"])


def get_documents_service(
    library_id: UUID,
    db: Persistence = Depends(),
    lock_manager: LockManager = Depends(),
) -> DocumentsService:
    return DocumentsService(db, lock_manager)


@router.post("", response_model=Documents, status_code=status.HTTP_201_CREATED)
async def create_document(
    library_id: UUID,
    document: DocumentCreate,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Create a new document in a library."""
    created_document = documents_service.create_document(
        library_id=library_id,
        name=document.name,
        metadata=document.metadata,
    )
    if not created_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found",
        )
    return created_document


@router.get("/{document_id}", response_model=Documents)
async def get_document(
    library_id: UUID,
    document_id: UUID,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Get a document by ID."""
    document = documents_service.get_document(document_id)
    if not document or document.library_id != library_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.put("/{document_id}", response_model=Documents)
async def update_document(
    library_id: UUID,
    document_id: UUID,
    document: DocumentUpdate,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Update a document."""
    existing_document = documents_service.get_document(document_id)
    if not existing_document or existing_document.library_id != library_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    update_data = {}
    if document.name is not None:
        update_data["name"] = document.name
    if document.metadata is not None:
        update_data["metadata"] = document.metadata

    updated_document = documents_service.update_document(document_id=document_id, **update_data)
    return updated_document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    library_id: UUID,
    document_id: UUID,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """Delete a document."""
    existing_document = documents_service.get_document(document_id)
    if not existing_document or existing_document.library_id != library_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if not documents_service.delete_document(document_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document",
        )


@router.get("", response_model=List[Documents])
async def list_documents(
    library_id: UUID,
    documents_service: DocumentsService = Depends(get_documents_service),
):
    """List all documents in a library."""
    return documents_service.list_documents(library_id)
