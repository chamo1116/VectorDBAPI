from heapq import heappop, heappush
from typing import Dict, List, Optional, Tuple

from app.core.indexing.indexing_algorithm import IndexingAlgorithm
from app.core.models.chunks import Chunks


class BruteForceIndex(IndexingAlgorithm):
    """
    Brute Force index implementation with cosine similarity.
    Time complexity: O(N) for search
    Space complexity: O(N)
    Simple but not scalable for large datasets.
    """

    def __init__(self):
        self.chunks = []

    def index(self, chunks: List[Chunks]) -> None:
        self.chunks = chunks

    def query(
        self,
        embedding: List[float],
        k: int,
        filters: Optional[Dict] = None,
    ) -> List[Tuple[Chunks, float]]:
        filtered_chunks = self._apply_filters(self.chunks, filters)

        # Calculate distances for all chunks
        distances = []
        for chunk in filtered_chunks:
            distance = self._euclidean_distance(embedding, chunk.embedding)

            # Push to heap (using similarity as key)
            if len(distances) < k:
                heappush(distances, (-distance, chunk))
            else:
                if distance < -distances[0][0]:  # Compare with current worst
                    heappop(distances)
                    heappush(distances, (-distance, chunk))

        # Extract results in descending order of similarity
        results = sorted([(-dist, chunk) for dist, chunk in distances], key=lambda x: x[0])
        return [(chunk, similarity) for similarity, chunk in results]
