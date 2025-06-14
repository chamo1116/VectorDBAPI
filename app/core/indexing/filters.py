from datetime import datetime
from typing import Optional

from app.core.models.chunks import Chunks


class Filters:

    def __init__(self, key: str) -> None:
        self.filters_mapper = {
            "created_after": self._filter_created_after,
            "text_contains": self._text_contains,
        }
        self.filter_function = self.filters_mapper.get(key)

    def is_a_valid_chunk(self, chunk: Chunks, key: Optional[str], value: str) -> bool:
        if not self.filter_function:
            return False
        return self.filter_function(chunk, key, value)

    def _filter_created_after(self, chunk: Chunks, _, value: str) -> bool:
        if chunk.created_at <= datetime.fromisoformat(value):
            return False

        return True

    def _text_contains(self, chunk: Chunks, key: Optional[str], value: str) -> bool:
        if key in chunk.metadata and chunk.metadata[key] != value:
            return False
        return True
