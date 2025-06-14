from app.core.indexing import INDEX_IMPLEMENTATIONS
from app.core.indexing.brute_force_index import BruteForceIndex
from app.infrastructure.locking import LockManager
from app.infrastructure.persistence import Persistence


class BaseService:
    def __init__(
        self,
        db: Persistence,
        lock_manager: LockManager,
    ):
        self.db = db
        self.lock_manager = lock_manager
        self.index_strategy = BruteForceIndex()

    def _set_index_strategy(self, strategy: str):
        index_strategy = INDEX_IMPLEMENTATIONS.get(strategy)
        if not index_strategy:
            raise ValueError(f"Unknown index strategy: {strategy}")
        self.index_strategy = index_strategy
