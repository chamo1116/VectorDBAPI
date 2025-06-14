# type:ignore
from uuid import uuid4

import pytest
from fastapi import status


def test_create_library(test_client, sample_library_data):
    response = test_client.post("/libraries/", json=sample_library_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == sample_library_data["name"]
    assert data["description"] == sample_library_data["description"]
    assert data["metadata"] == sample_library_data["metadata"]
    assert "id" in data


def test_create_library_missing_name(test_client):
    response = test_client.post("/libraries/", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_library(test_client, created_library):
    library_id = created_library["id"]
    response = test_client.get(f"/libraries/{library_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == library_id
    assert data["name"] == created_library["name"]


def test_get_nonexistent_library(test_client):
    response = test_client.get(f"/libraries/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_libraries(test_client, created_library):
    response = test_client.get("/libraries/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(lib["id"] == created_library["id"] for lib in data)


def test_update_library(test_client, created_library):
    library_id = created_library["id"]
    update_data = {
        "name": "Updated Library",
        "description": "Updated Description",
        "metadata": {"updated": "true"},
    }
    response = test_client.put(f"/libraries/{library_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == library_id
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["metadata"] == update_data["metadata"]


def test_update_nonexistent_library(test_client):
    update_data = {"name": "Updated Library"}
    response = test_client.put(f"/libraries/{uuid4()}", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_library_partial(test_client, created_library):
    library_id = created_library["id"]
    # Only update name
    update_data = {"name": "Partially Updated"}
    response = test_client.put(f"/libraries/{library_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == library_id
    assert data["name"] == update_data["name"]
    assert data["description"] == created_library["description"]  # Unchanged
    assert data["metadata"] == created_library["metadata"]  # Unchanged


def test_delete_library(test_client, created_library):
    library_id = created_library["id"]
    response = test_client.delete(f"/libraries/{library_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify library is deleted
    get_response = test_client.get(f"/libraries/{library_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_library(test_client):
    response = test_client.delete(f"/libraries/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_index_library(test_client, created_library, created_document, created_chunk):
    library_id = created_library["id"]
    response = test_client.post(f"/libraries/{library_id}/index")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert "message" in data


def test_index_nonexistent_library(test_client):
    response = test_client.post(f"/libraries/{uuid4()}/index")
    assert response.status_code == status.HTTP_404_NOT_FOUND
