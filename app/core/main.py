from fastapi import FastAPI

from app.core.api.routers import chunks, documents, libraries
from app.infrastructure.locking import LockManager
from app.infrastructure.persistence import Persistence

app = FastAPI(
    title="Vector Database API",
    description="REST API for vector document storage and search",
    version="0.1.0",
)

# Initialize dependencies
db = Persistence()
lock_manager = LockManager()

# Include routers
app.include_router(libraries.router, prefix="/libraries", tags=["libraries"])
app.include_router(
    chunks.router,
    prefix="/libraries/{library_id}/documents/{document_id}",
    tags=["chunks"],
)
app.include_router(documents.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
