import math
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from app.core.indexing.filters import Filters
from app.core.models.chunks import Chunks


class IndexingAlgorithm(ABC):

    @abstractmethod
    def index(self, chunks: List[Chunks]) -> None:
        raise NotImplementedError

    @abstractmethod
    def query(
        self, embedding: List[float], k: int, filters: Optional[Dict] = None
    ) -> List[Tuple[Chunks, float]]:
        raise NotImplementedError

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def _euclidean_distance(self, a: List[float], b: List[float]) -> float:
        squared_distance = sum((x - y) ** 2 for x, y in zip(a, b))
        return math.sqrt(squared_distance)

    def _apply_filters(self, chunks: List[Chunks], filters: Optional[Dict]) -> List[Chunks]:
        if not filters:
            return chunks

        filtered = []

        for chunk in chunks:
            is_matched = True

            for key, value in filters.items():
                filter = Filters(key)
                is_matched = filter.is_a_valid_chunk(chunk, key, value)
                if not is_matched:
                    break
            if is_matched:
                filtered.append(chunk)

        return filtered if filtered else chunks
