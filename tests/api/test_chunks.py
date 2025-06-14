# type:ignore
from uuid import uuid4

import pytest
from fastapi import status


def test_create_chunk(test_client, created_library, created_document, sample_chunk_data):
    library_id = created_library["id"]
    document_id = created_document["id"]

    response = test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks",
        json=sample_chunk_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["text"] == sample_chunk_data["text"]
    assert data["embedding"] == sample_chunk_data["embedding"]
    assert data["metadata"] == sample_chunk_data["metadata"]
    assert "id" in data


def test_create_chunk_missing_required_fields(test_client, created_library, created_document):
    library_id = created_library["id"]
    document_id = created_document["id"]

    # Missing text and embedding
    response = test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks",
        json={"metadata": {"key": "value"}},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_chunk_nonexistent_library(test_client, created_document, sample_chunk_data):
    document_id = created_document["id"]

    response = test_client.post(
        f"/libraries/{uuid4()}/documents/{document_id}/chunks", json=sample_chunk_data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_chunk_nonexistent_document(test_client, created_library, sample_chunk_data):
    library_id = created_library["id"]

    response = test_client.post(f"/libraries/{library_id}/documents/{uuid4()}/chunks", json=sample_chunk_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_chunks(test_client, created_library, created_document, created_chunk):
    library_id = created_library["id"]
    document_id = created_document["id"]

    response = test_client.get(f"/libraries/{library_id}/documents/{document_id}/chunks")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(chunk["id"] == created_chunk["id"] for chunk in data)


def test_list_chunks_nonexistent_library(test_client, created_document):
    document_id = created_document["id"]

    response = test_client.get(f"/libraries/{uuid4()}/documents/{document_id}/chunks")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_chunk(test_client, created_library, created_document, created_chunk):
    library_id = created_library["id"]
    document_id = created_document["id"]
    chunk_id = created_chunk["id"]

    response = test_client.get(f"/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == chunk_id
    assert data["text"] == created_chunk["text"]
    assert data["embedding"] == created_chunk["embedding"]
    assert data["metadata"] == created_chunk["metadata"]


def test_get_nonexistent_chunk(test_client, created_library, created_document):
    library_id = created_library["id"]
    document_id = created_document["id"]

    response = test_client.get(f"/libraries/{library_id}/documents/{document_id}/chunks/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_chunk(test_client, created_library, created_document, created_chunk):
    library_id = created_library["id"]
    document_id = created_document["id"]
    chunk_id = created_chunk["id"]

    update_data = {
        "text": "Updated text",
        "embedding": [0.4, 0.5, 0.6],
        "metadata": {"updated": "true"},
    }

    response = test_client.put(
        f"/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}",
        json=update_data,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == chunk_id
    assert data["text"] == update_data["text"]
    assert data["embedding"] == update_data["embedding"]
    assert data["metadata"] == update_data["metadata"]


def test_update_chunk_partial(test_client, created_library, created_document, created_chunk):
    library_id = created_library["id"]
    document_id = created_document["id"]
    chunk_id = created_chunk["id"]

    # Only update text
    update_data = {"text": "Partially updated text"}

    response = test_client.put(
        f"/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}",
        json=update_data,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == chunk_id
    assert data["text"] == update_data["text"]
    assert data["embedding"] == created_chunk["embedding"]  # Unchanged
    assert data["metadata"] == created_chunk["metadata"]  # Unchanged


def test_update_nonexistent_chunk(test_client, created_library, created_document):
    library_id = created_library["id"]
    document_id = created_document["id"]

    update_data = {"text": "Updated text"}
    response = test_client.put(
        f"/libraries/{library_id}/documents/{document_id}/chunks/{uuid4()}",
        json=update_data,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_chunk(test_client, created_library, created_document, created_chunk):
    library_id = created_library["id"]
    document_id = created_document["id"]
    chunk_id = created_chunk["id"]

    response = test_client.delete(f"/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify chunk is deleted
    get_response = test_client.get(f"/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_chunk(test_client, created_library, created_document):
    library_id = created_library["id"]
    document_id = created_document["id"]

    response = test_client.delete(f"/libraries/{library_id}/documents/{document_id}/chunks/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_search_chunks(test_client, created_library, created_document, created_chunk):
    library_id = created_library["id"]
    document_id = created_document["id"]

    # First index the library
    test_client.post(f"/libraries/{library_id}/index")

    search_data = {"embedding": [0.1, 0.2, 0.3], "k": 5, "filters": {"key": "value"}}

    response = test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks/search",
        json=search_data,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "chunk" in data[0]
    assert "similarity" in data[0]


def test_search_chunks_unindexed_library(test_client, created_library, created_document):
    library_id = created_library["id"]
    document_id = created_document["id"]

    search_data = {"embedding": [0.1, 0.2, 0.3], "k": 5}

    response = test_client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks/search",
        json=search_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
