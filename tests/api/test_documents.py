# type:ignore
from typing import Dict
from uuid import UUID, uuid4

import pytest
from fastapi import status

from app.core.models.chunks import Chunks
from app.core.models.documents import Documents
from app.core.services.documents import DocumentsService
from app.core.services.libraries import LibrariesService
from app.infrastructure.locking import LockManager
from app.infrastructure.persistence import Persistence


@pytest.fixture
def persistence():
    return Persistence()


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
def sample_library_id():
    return uuid4()


@pytest.fixture
def sample_document_data():
    return {
        "name": "Test Document",
        "metadata": {"type": "test", "category": "example"},
    }


def test_create_document(documents_service, libraries_service, sample_library_id, sample_document_data):
    """Test creating a document in an existing library."""
    # First create a library
    library = libraries_service.create_library(name="Test Library", metadata={"type": "test"})

    # Create document
    document = documents_service.create_document(
        library_id=library.id,
        name=sample_document_data["name"],
        metadata=sample_document_data["metadata"],
    )

    assert document is not None
    assert document.name == sample_document_data["name"]
    assert document.metadata == sample_document_data["metadata"]
    assert document.library_id == library.id
    assert isinstance(document.chunks, list)
    assert len(document.chunks) == 0


def test_create_document_nonexistent_library(documents_service, sample_document_data):
    """Test creating a document in a nonexistent library."""
    document = documents_service.create_document(
        library_id=uuid4(),
        name=sample_document_data["name"],
        metadata=sample_document_data["metadata"],
    )

    assert document is None


def test_get_document(documents_service, libraries_service, sample_library_id, sample_document_data):
    """Test retrieving a document by ID."""
    # First create a library and document
    library = libraries_service.create_library(name="Test Library", metadata={"type": "test"})

    document = documents_service.create_document(
        library_id=library.id,
        name=sample_document_data["name"],
        metadata=sample_document_data["metadata"],
    )

    # Get document
    retrieved_document = documents_service.get_document(document.id)

    assert retrieved_document is not None
    assert retrieved_document.id == document.id
    assert retrieved_document.name == document.name
    assert retrieved_document.metadata == document.metadata
    assert isinstance(retrieved_document.chunks, list)
    assert len(retrieved_document.chunks) == 0


def test_get_nonexistent_document(documents_service):
    """Test retrieving a nonexistent document."""
    document = documents_service.get_document(uuid4())
    assert document is None


def test_update_document(documents_service, libraries_service, sample_library_id, sample_document_data):
    """Test updating a document."""
    # First create a library and document
    library = libraries_service.create_library(name="Test Library", metadata={"type": "test"})

    document = documents_service.create_document(
        library_id=library.id,
        name=sample_document_data["name"],
        metadata=sample_document_data["metadata"],
    )

    # Update document
    updated_name = "Updated Document"
    updated_metadata: Dict[str, str] = {"type": "updated", "category": "test"}

    updated_document = documents_service.update_document(
        document_id=document.id, name=updated_name, metadata=updated_metadata
    )

    assert updated_document is not None
    assert updated_document.id == document.id
    assert updated_document.name == updated_name
    assert updated_document.metadata == updated_metadata
    assert isinstance(updated_document.chunks, list)
    assert len(updated_document.chunks) == 0


def test_update_nonexistent_document(documents_service):
    """Test updating a nonexistent document."""
    updated_document = documents_service.update_document(
        document_id=uuid4(), name="Updated Document", metadata={"type": "updated"}
    )
    assert updated_document is None


def test_delete_document(documents_service, libraries_service, sample_library_id, sample_document_data):
    """Test deleting a document."""
    # First create a library and document
    library = libraries_service.create_library(name="Test Library", metadata={"type": "test"})

    document = documents_service.create_document(
        library_id=library.id,
        name=sample_document_data["name"],
        metadata=sample_document_data["metadata"],
    )

    # Delete document
    assert documents_service.delete_document(document.id) is True

    # Verify document is deleted
    deleted_document = documents_service.get_document(document.id)
    assert deleted_document is None


def test_delete_nonexistent_document(documents_service):
    """Test deleting a nonexistent document."""
    assert documents_service.delete_document(uuid4()) is False


def test_list_documents(documents_service, libraries_service, sample_library_id):
    """Test listing all documents in a library."""
    # First create a library
    library = libraries_service.create_library(name="Test Library", metadata={"type": "test"})

    # Create multiple documents
    documents = []
    for i in range(3):
        document = documents_service.create_document(
            library_id=library.id, name=f"Test Document {i}", metadata={"index": str(i)}
        )
        assert document is not None
        documents.append(document)

    # List documents
    listed_documents = documents_service.list_documents(library.id)

    assert len(listed_documents) == 3
    for i, doc in enumerate(listed_documents):
        assert doc.name == f"Test Document {i}"
        assert doc.metadata == {"index": str(i)}
        assert isinstance(doc.chunks, list)
        assert len(doc.chunks) == 0


def test_list_documents_empty_library(documents_service, libraries_service):
    """Test listing documents in an empty library."""
    # Create an empty library
    library = libraries_service.create_library(name="Empty Library", metadata={"type": "test"})

    # List documents
    documents = documents_service.list_documents(library.id)

    assert len(documents) == 0
