# type:ignore
from datetime import datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.main import app
from app.core.services.documents import DocumentsService
from app.infrastructure.locking import LockManager
from app.infrastructure.persistence import Persistence


@pytest.fixture
def test_db():
    db = Persistence(storage_dir=":memory:")
    yield db
    # Cleanup after tests
    db.libraries.clear()
    db.documents.clear()
    db.chunks.clear()
    db.save()


@pytest.fixture
def lock_manager():
    return LockManager()


@pytest.fixture
def test_client(test_db, lock_manager):
    # Override dependencies for testing
    app.dependency_overrides[Persistence] = lambda: test_db
    app.dependency_overrides[LockManager] = lambda: lock_manager
    client = TestClient(app)
    yield client
    # Cleanup dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_library_data():
    return {
        "name": "Test Library",
        "description": "Test Description",
        "metadata": {"key": "value"},
    }


@pytest.fixture
def sample_document_data():
    return {"name": "Test Document", "metadata": {"doc_key": "doc_value"}}


@pytest.fixture
def sample_chunk_data():
    return {
        "text": "Sample text content",
        "embedding": [0.1, 0.2, 0.3],
        "metadata": {"chunk_key": "chunk_value"},
    }


@pytest.fixture
def created_library(test_client, sample_library_data):
    response = test_client.post("/libraries/", json=sample_library_data)
    return response.json()


@pytest.fixture
def created_document(test_client, created_library, sample_document_data, test_db, lock_manager):
    library_id = created_library["id"]
    doc_service = DocumentsService(test_db, lock_manager)
    document = doc_service.add_document(UUID(library_id), **sample_document_data)
    return document.model_dump()


@pytest.fixture
def created_chunk(test_client, created_library, created_document, sample_chunk_data):
    library_id = created_library["id"]
    document_id = created_document["id"]
    response = test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks",
        json=sample_chunk_data,
    )
    return response.json()
