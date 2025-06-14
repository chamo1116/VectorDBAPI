from .brute_force_index import BruteForceIndex
from .kdtree_index import KDTreeIndex

INDEX_IMPLEMENTATIONS = {
    "bruteforce": BruteForceIndex(),
    "kdtree": KDTreeIndex(),
    "default": BruteForceIndex(),
}
