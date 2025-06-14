# type:ignore
from uuid import uuid4

import pytest
from fastapi import status

from app.core.models.documents import Chunks, Documents
from app.core.models.libraries import Libraries
from app.core.services.documents import DocumentsService
from app.core.services.libraries import LibrariesService
from app.infrastructure.locking import LockManager


def test_create_library(test_db, lock_manager):
    service = LibrariesService(test_db, lock_manager)
    library = service.create_library("Test Library")

    assert isinstance(library, Libraries)
    assert library.name == "Test Library"
    assert library.id in test_db.libraries


def test_get_library(test_db, lock_manager):
    service = LibrariesService(test_db, lock_manager)
    created_lib = service.create_library("Test Library")
    retrieved_lib = service.get_library(created_lib.id)

    assert retrieved_lib == created_lib


def test_get_nonexistent_library(test_db, lock_manager):
    service = LibrariesService(test_db, lock_manager)
    assert service.get_library(uuid4()) is None


def test_update_library(test_db, lock_manager):
    service = LibrariesService(test_db, lock_manager)
    library = service.create_library("Old Name")

    updated = service.update_library(library.id, name="New Name")
    assert updated.name == "New Name"
    assert test_db.libraries[library.id].name == "New Name"


def test_delete_library(test_db, lock_manager):
    service = LibrariesService(test_db, lock_manager)
    library = service.create_library("To Delete")

    assert service.delete_library(library.id)
    assert library.id not in test_db.libraries


def test_list_libraries(test_db, lock_manager):
    service = LibrariesService(test_db, lock_manager)
    lib1 = service.create_library("Lib 1")
    lib2 = service.create_library("Lib 2")

    libraries = service.list_libraries()
    assert len(libraries) == 2
    assert lib1 in libraries
    assert lib2 in libraries


def test_index_libraries(test_db, lock_manager):
    # Create services
    library_service = LibrariesService(test_db, lock_manager)
    document_service = DocumentsService(test_db, lock_manager)

    # Create library
    library = library_service.create_library("Index library")

    # Create document with chunks
    document = document_service.create_document(
        library_id=library.id, name="Test Document", metadata={"key": "value"}
    )

    # Add chunks to the document
    chunk = Chunks(
        text="Sample text content",
        embedding=[0.1, 0.2, 0.3],
        metadata={"chunk_key": "chunk_value"},
    )
    document.chunks.append(chunk)
    test_db.documents[document.id] = document

    # Add document to library
    library.documents.append(document)
    test_db.libraries[library.id] = library
    test_db.save()

    # Index the library
    success = library_service.index_library(library.id)
    assert success is True

    # Verify indexing
    indexed_lib = library_service.get_library(library.id)
    assert indexed_lib.is_indexed is True
