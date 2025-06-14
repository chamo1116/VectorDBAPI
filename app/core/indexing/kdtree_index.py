from collections import deque
from heapq import heappop, heappush
from typing import Dict, List, Optional, Set, Tuple

from app.core.indexing.indexing_algorithm import IndexingAlgorithm
from app.core.models.chunks import Chunks


class KDTreeIndex(IndexingAlgorithm):
    """KD-Tree implementation for faster kNN searches"""

    def __init__(self):
        self.tree = None
        self.chunks = []
        self.dimension = 0

    def index(self, chunks: List[Chunks]) -> None:
        if not chunks:
            self.tree = None
            return

        self.chunks = chunks
        self.dimension = len(chunks[0].embedding)
        points = [(i, chunk.embedding) for i, chunk in enumerate(chunks)]
        self.tree = self._build_kdtree(points)

    def query(
        self,
        embedding: List[float],
        k: int,
        filters: Optional[Dict] = None,
    ) -> Optional[List[Tuple[Chunks, float]]]:
        if not self.tree or k <= 0:
            return []

        # Check if embedding dimension matches the indexed embeddings
        if len(embedding) != self.dimension:
            raise IndexError(
                f"Query embedding dimension {len(embedding)} does not match indexed embeddings dimension {self.dimension}"
            )

        filtered_chunks = self._apply_filters(self.chunks, filters)

        valid_indices = {index for index in range(len(filtered_chunks))}

        if not filtered_chunks:
            return []

        self.index(filtered_chunks)

        return self._nearest_neighbors(embedding, k, valid_indices)

    def _build_kdtree(self, points: List[Tuple[int, List[float]]], depth=0):
        if not points:
            return None

        axis = depth % self.dimension

        # Sort points and choose median
        points.sort(key=lambda x: x[1][axis])
        median = len(points) // 2

        return {
            "point_idx": points[median][0],
            "point": points[median][1],
            "axis": axis,
            "left": self._build_kdtree(points[:median], depth + 1),
            "right": self._build_kdtree(points[median + 1 :], depth + 1),
        }

    def _nearest_neighbors(self, embedding: List[float], k: int, valid_indices: Set[int]) -> Optional[List]:
        # Use a max-heap to keep track of k nearest neighbors (store negative distances)
        best = []

        # Stack for iterative traversal: (node, depth)
        stack = deque([(self.tree, 0)])

        while stack:
            node, depth = stack.pop()

            # Skip if node is None or doesn't contain valid points
            if node is None:
                continue

            point_idx = node["point_idx"]
            axis = node["axis"]

            # Only process if point is valid
            if point_idx in valid_indices:
                # Calculate cosine similarity (we want highest similarity)
                similarity = self._cosine_similarity(embedding, node["point"])

                # Maintain k most similar neighbors
                if len(best) < k:
                    heappush(best, (similarity, point_idx))
                else:
                    if similarity > best[0][0]:
                        heappop(best)
                        heappush(best, (similarity, point_idx))

            # Determine which side to explore first
            if embedding[axis] < node["point"][axis]:
                near, far = node["left"], node["right"]
            else:
                near, far = node["right"], node["left"]

            # Push far side first (will be processed after near side)
            if far is not None:
                stack.append((far, depth + 1))

            # Only explore near side if necessary
            if near is not None:
                stack.append((near, depth + 1))

        # Convert to results with chunks and similarities
        results = []
        for similarity, idx in sorted(best, key=lambda x: -x[0]):  # Sort by descending similarity
            results.append((self.chunks[idx], similarity))

        return results[:k]
