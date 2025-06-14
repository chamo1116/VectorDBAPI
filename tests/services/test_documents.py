# type:ignore
import time
from datetime import datetime
from typing import Dict
from uuid import UUID, uuid4

import pytest

from app.core.models.chunks import Chunks
from app.core.models.documents import Documents
from app.core.services.documents import DocumentsService
from app.core.services.libraries import LibrariesService
from app.infrastructure.locking import LockManager
from app.infrastructure.persistence import Persistence


@pytest.fixture
def persistence():
    return Persistence(storage_dir="test_data")


@pytest.fixture
def lock_manager():
    return LockManager()


@pytest.fixture
def documents_service(persistence, lock_manager):
    return DocumentsService(persistence, lock_manager)


@pytest.fixture
def libraries_service(persistence, lock_manager):
    return LibrariesService(persistence, lock_manager)


@pytest.fixture
def sample_library(libraries_service):
    library = libraries_service.create_library(name="Test Library", metadata={"type": "test"})
    return library


def test_create_document(documents_service, sample_library):
    # Test successful creation
    document = documents_service.create_document(
        library_id=sample_library.id,
        name="Test Document",
        metadata={"key": "value"},
    )
    assert document is not None
    assert document.name == "Test Document"
    assert document.metadata == {"key": "value"}
    assert document.library_id == sample_library.id
    assert isinstance(document.id, UUID)
    assert isinstance(document.created_at, datetime)
    assert isinstance(document.updated_at, datetime)
    assert isinstance(document.chunks, list)
    assert len(document.chunks) == 0

    # Test creation with minimal data
    document = documents_service.create_document(library_id=sample_library.id, name="Minimal Document")
    assert document is not None
    assert document.name == "Minimal Document"
    assert document.metadata == {}
    assert isinstance(document.chunks, list)
    assert len(document.chunks) == 0


def test_get_document(documents_service, sample_library):
    # Create a document first
    created = documents_service.create_document(library_id=sample_library.id, name="Test Document")
    assert created is not None

    # Test successful retrieval
    retrieved = documents_service.get_document(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == "Test Document"
    assert isinstance(retrieved.chunks, list)
    assert len(retrieved.chunks) == 0

    # Test non-existent document
    non_existent = documents_service.get_document(uuid4())
    assert non_existent is None


def test_update_document(documents_service, sample_library):
    # Create a document first
    document = documents_service.create_document(
        library_id=sample_library.id,
        name="Original Name",
        metadata={"original": "value"},
    )
    assert document is not None

    # Test successful update
    updated = documents_service.update_document(
        document.id,
        name="Updated Name",
        metadata={"updated": "value"},
    )
    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.metadata == {"updated": "value"}
    assert isinstance(updated.chunks, list)
    assert len(updated.chunks) == 0

    # Test non-existent document
    non_existent = documents_service.update_document(uuid4(), name="Won't Update")
    assert non_existent is None


def test_delete_document(documents_service, sample_library):
    # Create a document first
    document = documents_service.create_document(library_id=sample_library.id, name="To Delete")
    assert document is not None

    # Test successful deletion
    assert documents_service.delete_document(document.id) is True
    assert documents_service.get_document(document.id) is None

    # Test non-existent document
    assert documents_service.delete_document(uuid4()) is False


def test_list_documents(documents_service, sample_library):
    # Clean up any existing documents
    for doc in documents_service.list_documents():
        documents_service.delete_document(doc.id)

    # Create multiple documents
    documents = []
    for i in range(3):
        document = documents_service.create_document(
            library_id=sample_library.id,
            name=f"Document {i}",
            metadata={"index": str(i)},
        )
        assert document is not None
        documents.append(document)

    # Test listing all documents
    listed = documents_service.list_documents()
    assert len(listed) == 3
    assert all(isinstance(doc, Documents) for doc in listed)
    assert all(doc.name.startswith("Document") for doc in listed)
    assert all(isinstance(doc.metadata.get("index"), str) for doc in listed)
    assert all(isinstance(doc.chunks, list) for doc in listed)
    assert all(len(doc.chunks) == 0 for doc in listed)

    # Test listing documents for specific library
    library_docs = documents_service.list_documents(sample_library.id)
    assert len(library_docs) == 3
    assert all(doc.library_id == sample_library.id for doc in library_docs)

    # Test listing documents for non-existent library
    other_library_id = uuid4()
    empty_list = documents_service.list_documents(other_library_id)
    assert len(empty_list) == 0

    # Clean up after test
    for doc in documents:
        documents_service.delete_document(doc.id)
