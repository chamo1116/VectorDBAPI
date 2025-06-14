# type:ignore
from uuid import uuid4

import pytest

from app.core.indexing.kdtree_index import KDTreeIndex
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
    index = KDTreeIndex()
    index.index(sample_chunks)
    assert len(index.chunks) == len(sample_chunks)
    assert index.tree is not None
    assert index.dimension == 3  # 3D embeddings


def test_index_empty_chunks():
    index = KDTreeIndex()
    index.index([])
    assert len(index.chunks) == 0
    assert index.tree is None


def test_build_kdtree(sample_chunks):
    index = KDTreeIndex()
    index.index(sample_chunks)

    # Verify tree structure
    assert "point_idx" in index.tree
    assert "point" in index.tree
    assert "axis" in index.tree
    assert "left" in index.tree
    assert "right" in index.tree

    # Verify point indices are valid
    def verify_tree_structure(node):
        if node is None:
            return
        assert isinstance(node["point_idx"], int)
        assert 0 <= node["point_idx"] < len(sample_chunks)
        assert isinstance(node["point"], list)
        assert len(node["point"]) == 3  # 3D embeddings
        verify_tree_structure(node["left"])
        verify_tree_structure(node["right"])

    verify_tree_structure(index.tree)


def test_query_without_filters(sample_chunks):
    index = KDTreeIndex()
    index.index(sample_chunks)

    # Query with embedding similar to first chunk
    query_embedding = [0.1, 0.2, 0.3]
    results = index.query(query_embedding, k=2)

    assert results is not None
    assert len(results) == 2
    # Verify the chunks are in the results
    chunk_texts = {result[0].text for result in results}
    assert "First chunk" in chunk_texts
    assert "Second chunk" in chunk_texts or "Third chunk" in chunk_texts


def test_query_with_filters(sample_chunks):
    index = KDTreeIndex()
    index.index(sample_chunks)

    # Query with filters
    query_embedding = [0.1, 0.2, 0.3]
    filters = {"text_contains": "value2"}
    results = index.query(query_embedding, k=2, filters=filters)

    assert results is not None
    assert len(results) == 1
    assert results[0][0].text == "Second chunk"


def test_query_empty_index():
    index = KDTreeIndex()
    results = index.query([0.1, 0.2, 0.3], k=2)
    assert results == []


def test_query_k_larger_than_chunks(sample_chunks):
    index = KDTreeIndex()
    index.index(sample_chunks)

    results = index.query([0.1, 0.2, 0.3], k=5)
    assert len(results) == len(sample_chunks)


def test_query_k_zero(sample_chunks):
    index = KDTreeIndex()
    index.index(sample_chunks)

    results = index.query([0.1, 0.2, 0.3], k=0)
    assert results == []


def test_query_with_invalid_embedding_dimension(sample_chunks):
    index = KDTreeIndex()
    index.index(sample_chunks)

    # Query with wrong dimension embedding
    query_embedding = [0.1, 0.2]  # 2D instead of 3D
    with pytest.raises(IndexError):
        index.query(query_embedding, k=2)


def test_nearest_neighbors_ordering(sample_chunks):
    index = KDTreeIndex()
    index.index(sample_chunks)

    # Query with embedding similar to first chunk
    query_embedding = [0.1, 0.2, 0.3]
    results = index.query(query_embedding, k=3)

    assert results is not None
    assert len(results) == 3

    # Verify results are ordered by similarity (highest first)
    similarities = [result[1] for result in results]
    assert similarities == sorted(similarities, reverse=True)


def test_nearest_neighbors_with_duplicate_embeddings():
    chunks = [
        Chunks(
            id=uuid4(),
            text="Chunk 1",
            embedding=[0.1, 0.2, 0.3],
            metadata={"text_contains": "value1"},
        ),
        Chunks(
            id=uuid4(),
            text="Chunk 2",
            embedding=[0.1, 0.2, 0.3],  # Same embedding as Chunk 1
            metadata={"text_contains": "value2"},
        ),
    ]

    index = KDTreeIndex()
    index.index(chunks)

    results = index.query([0.1, 0.2, 0.3], k=2)
    assert results is not None
    assert len(results) == 2
    # Both chunks should be returned with same similarity
    assert results[0][1] == results[1][1]
