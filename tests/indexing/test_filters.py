from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.core.indexing.filters import Filters
from app.core.models.chunks import Chunks


@pytest.fixture
def sample_chunk():
    return Chunks(
        id=uuid4(),
        text="Sample text",
        embedding=[0.1, 0.2, 0.3],
        metadata={"key": "value"},
        created_at=datetime.now(),
    )


def test_filter_created_after(sample_chunk):
    filter = Filters("created_after")

    # Test with date before chunk creation
    past_date = (sample_chunk.created_at - timedelta(days=1)).isoformat()
    assert filter.is_a_valid_chunk(sample_chunk, "created_after", past_date) is True

    # Test with date after chunk creation
    future_date = (sample_chunk.created_at + timedelta(days=1)).isoformat()
    assert filter.is_a_valid_chunk(sample_chunk, "created_after", future_date) is False


def test_text_contains(sample_chunk):
    filter = Filters("text_contains")

    # Test with matching metadata
    assert filter.is_a_valid_chunk(sample_chunk, "key", "value") is True

    # Test with non-matching metadata
    assert filter.is_a_valid_chunk(sample_chunk, "key", "different_value") is False

    # Test with non-existent key
    assert filter.is_a_valid_chunk(sample_chunk, "nonexistent_key", "value") is True


def test_invalid_filter_key(sample_chunk):
    filter = Filters("invalid_key")
    assert filter.is_a_valid_chunk(sample_chunk, "any_key", "any_value") is False
