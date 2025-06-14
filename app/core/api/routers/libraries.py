from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.core.models.libraries import Libraries
from app.core.services.libraries import LibrariesService
from app.infrastructure.locking import LockManager
from app.infrastructure.persistence import Persistence

router = APIRouter()


def get_library_service(
    db: Persistence = Depends(Persistence),
    lock_manager: LockManager = Depends(LockManager),
) -> LibrariesService:
    return LibrariesService(db, lock_manager)


@router.post(
    "/",
    response_model=Libraries,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new library",
    description="Creates a new library with the given name and optional description/metadata",
)
async def create_library(
    name: str = Body(...),
    description: Optional[str] = Body(None),
    metadata: Optional[dict] = Body(None),
    service: LibrariesService = Depends(get_library_service),
):
    return service.create_library(name, description, metadata)


@router.get(
    "/",
    response_model=List[Libraries],
    summary="List all libraries",
    description="Returns a list of all available libraries",
)
async def list_libraries(service: LibrariesService = Depends(get_library_service)):
    return service.list_libraries()


@router.get(
    "/{library_id}",
    response_model=Libraries,
    summary="Get library details",
    description="Returns details for a specific library",
)
async def get_library(library_id: UUID, service: LibrariesService = Depends(get_library_service)):
    library = service.get_library(library_id)
    if not library:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Library not found")
    return library


@router.put(
    "/{library_id}",
    response_model=Libraries,
    summary="Update library",
    description="Updates library information",
)
async def update_library(
    library_id: UUID,
    name: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    metadata: Optional[dict] = Body(None),
    service: LibrariesService = Depends(get_library_service),
):
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if metadata is not None:
        update_data["metadata"] = metadata

    library = service.update_library(library_id, **update_data)
    if not library:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Library not found")
    return library


@router.delete(
    "/{library_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete library",
    description="Deletes a library and all its contents",
)
async def delete_library(library_id: UUID, service: LibrariesService = Depends(get_library_service)):
    success = service.delete_library(library_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Library not found")


@router.post(
    "/{library_id}/index",
    summary="Index library",
    description="Indexes all chunks in the library for searching",
    responses={
        200: {"description": "Library indexed successfully"},
        404: {"description": "Library not found"},
    },
)
async def index_library(library_id: UUID, service: LibrariesService = Depends(get_library_service)):
    success = service.index_library(library_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Library not found")
    return {"success": True, "message": "Library indexed successfully"}
