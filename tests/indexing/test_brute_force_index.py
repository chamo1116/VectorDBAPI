# type:ignore
from uuid import uuid4

import pytest

from app.core.indexing.brute_force_index import BruteForceIndex
from app.core.models.chunks import Chunks


@pytest.fixture
def sample_chunks():
    return [
        Chunks(
            id=uuid4(),
            text="First chunk",
            embedding=[0.1, 0.2, 0.3],
            metadata={"text_contains": "value1"},
        ),
        Chunks(
            id=uuid4(),
            text="Second chunk",
            embedding=[0.4, 0.5, 0.6],
            metadata={"text_contains": "value2"},
        ),
        Chunks(
            id=uuid4(),
            text="Third chunk",
            embedding=[0.7, 0.8, 0.9],
            metadata={"text_contains": "value3"},
        ),
    ]


def test_index_chunks(sample_chunks):
    index = BruteForceIndex()
    index.index(sample_chunks)
    assert len(index.chunks) == len(sample_chunks)


def test_query_without_filters(sample_chunks):
    index = BruteForceIndex()
    index.index(sample_chunks)

    # Query with embedding similar to first chunk
    query_embedding = [0.1, 0.2, 0.3]
    results = index.query(query_embedding, k=2)

    assert len(results) == 2

    # Verify the chunks are in the results
    chunk_texts = {result[0].text for result in results}
    assert "First chunk" in chunk_texts
    assert "Second chunk" in chunk_texts or "Third chunk" in chunk_texts


def test_query_with_filters(sample_chunks):
    index = BruteForceIndex()
    index.index(sample_chunks)

    # Query with filters
    query_embedding = [0.1, 0.2, 0.3]
    filters = {"text_contains": "value2"}
    results = index.query(query_embedding, k=2, filters=filters)

    assert len(results) == 1
    assert results[0][0].text == "Second chunk"


def test_query_empty_index():
    index = BruteForceIndex()
    results = index.query([0.1, 0.2, 0.3], k=2)
    assert len(results) == 0


def test_query_k_larger_than_chunks(sample_chunks):
    index = BruteForceIndex()
    index.index(sample_chunks)

    results = index.query([0.1, 0.2, 0.3], k=5)
    assert len(results) == len(sample_chunks)


def test_cosine_similarity():
    index = BruteForceIndex()

    # Test identical vectors
    a = [1.0, 0.0, 0.0]
    b = [1.0, 0.0, 0.0]
    assert index._cosine_similarity(a, b) == 1.0

    # Test orthogonal vectors
    a = [1.0, 0.0, 0.0]
    b = [0.0, 1.0, 0.0]
    assert index._cosine_similarity(a, b) == 0.0

    # Test opposite vectors
    a = [1.0, 0.0, 0.0]
    b = [-1.0, 0.0, 0.0]
    assert index._cosine_similarity(a, b) == -1.0
