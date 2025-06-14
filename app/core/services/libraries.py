from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from app.core.models.libraries import Libraries
from app.core.services.base_service import BaseService
from app.infrastructure.locking import LockManager
from app.infrastructure.persistence import Persistence


class LibrariesService(BaseService):
    def __init__(self, db: Persistence, lock_manager: LockManager):
        super().__init__(db, lock_manager)

    def create_library(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Libraries:
        with self.lock_manager.write_lock("libraries"):
            library = Libraries(name=name, description=description, metadata=metadata or {})
            self.db.libraries[library.id] = library
            self.db.save()
            return library

    def get_library(self, library_id: UUID) -> Optional[Libraries]:
        with self.lock_manager.read_lock(f"library_{library_id}"):
            return self.db.libraries.get(library_id)

    def update_library(self, library_id: UUID, **kwargs) -> Optional[Libraries]:
        with self.lock_manager.write_lock(f"library_{library_id}"):
            library = self.db.libraries.get(library_id)
            if not library:
                return None

            for key, value in kwargs.items():
                if hasattr(library, key):
                    setattr(library, key, value)

            library.updated_at = datetime.now(timezone.utc)
            self.db.libraries[library.id] = library
            self.db.save()
            return library

    def delete_library(self, library_id: UUID) -> bool:
        with self.lock_manager.write_lock(f"library_{library_id}"):
            if library_id in self.db.libraries:
                del self.db.libraries[library_id]
                self.db.save()
                return True
            return False

    def list_libraries(self) -> List[Libraries]:
        with self.lock_manager.read_lock("libraries"):
            return list(self.db.libraries.values())

    def index_library(
        self,
        library_id: UUID,
        strategy: str = "default",
    ) -> bool:
        with self.lock_manager.write_lock(f"library_{library_id}"):
            library = self.db.libraries.get(library_id)
            if not library:
                return False

            all_chunks = []
            for doc in library.documents:
                if doc.chunks:  # Check if chunks exist
                    all_chunks.extend(doc.chunks)

            if not all_chunks:  # No chunks to index
                return False

            self._set_index_strategy(strategy)
            self.index_strategy.index(all_chunks)

            library.is_indexed = True
            library.updated_at = datetime.now(timezone.utc)
            self.db.libraries[library.id] = library
            self.db.save()
            return True
