# type: ignore
from uuid import uuid4

import pytest

from app.core.models.chunks import Chunks
from app.core.services.chunks import ChunksService
from app.core.services.documents import DocumentsService
from app.core.services.libraries import LibrariesService


def test_add_chunk(test_db, lock_manager):
    lib_service = LibrariesService(test_db, lock_manager)
    doc_service = DocumentsService(test_db, lock_manager)
    chunk_service = ChunksService(test_db, lock_manager)

    library = lib_service.create_library("Test Library")
    document = doc_service.add_document(library.id, "Test Doc")
    chunk = chunk_service.add_chunk(library.id, document.id, "Test text", [0.1, 0.2, 0.3])

    assert isinstance(chunk, Chunks)
    assert chunk.text == "Test text"
    assert chunk in document.chunks


def test_search_chunks(test_db, lock_manager):
    lib_service = LibrariesService(test_db, lock_manager)
    doc_service = DocumentsService(test_db, lock_manager)
    chunk_service = ChunksService(test_db, lock_manager)

    library = lib_service.create_library("Test Library")
    document = doc_service.add_document(library.id, "Test Doc")

    # Add multiple chunks with different embeddings
    chunk_service.add_chunk(library.id, document.id, "Text 1", [0.1, 0.1, 0.1])
    chunk_service.add_chunk(library.id, document.id, "Text 2", [0.9, 0.9, 0.9])

    # Index the library
    lib_service.index_library(library.id)

    # Search with query similar to first chunk
    results = chunk_service.search_chunks(library.id, [0.15, 0.15, 0.15], k=1)

    assert len(results) == 1
    assert results[0][0].text == "Text 1"
