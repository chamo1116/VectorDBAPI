from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from app.core.models.chunks import Chunks
from app.core.services.base_service import BaseService


class ChunksService(BaseService):

    def add_chunk(
        self,
        library_id: UUID,
        document_id: UUID,
        text: str,
        embedding: List,
        metadata: Optional[Dict] = None,
    ) -> Optional[Chunks]:
        with self.lock_manager.write_lock(f"library_{library_id}"):
            library = self.db.libraries.get(library_id)
            if not library:
                return None

            document = next((doc for doc in library.documents if doc.id == document_id), None)
            if not document:
                return None

            chunk = Chunks(text=text, embedding=embedding, metadata=metadata or {})
            document.chunks.append(chunk)
            document.updated_at = datetime.now(timezone.utc)
            library.updated_at = datetime.now(timezone.utc)
            library.is_indexed = False  # Invalidate index
            self.db.save()
            return chunk

    def get_chunk(self, library_id: UUID, document_id: UUID, chunk_id: UUID) -> Optional[Chunks]:
        with self.lock_manager.read_lock(f"library_{library_id}"):
            library = self.db.libraries.get(library_id)
            if not library:
                return None

            document = next((doc for doc in library.documents if doc.id == document_id), None)
            if not document:
                return None

            return next((ch for ch in document.chunks if ch.id == chunk_id), None)

    def update_chunk(
        self,
        library_id: UUID,
        document_id: UUID,
        chunk_id: UUID,
        text: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict] = None,
    ) -> Optional[Chunks]:
        with self.lock_manager.write_lock(f"library_{library_id}"):
            library = self.db.libraries.get(library_id)
            if not library:
                return None

            document = next((doc for doc in library.documents if doc.id == document_id), None)
            if not document:
                return None

            chunk = next((ch for ch in document.chunks if ch.id == chunk_id), None)
            if not chunk:
                return None

            if text is not None:
                chunk.text = text
            if embedding is not None:
                chunk.embedding = embedding
            if metadata is not None:
                chunk.metadata = metadata

            chunk.updated_at = datetime.utcnow()
            document.updated_at = datetime.utcnow()
            library.updated_at = datetime.utcnow()
            library.is_indexed = False
            self.db.save()
            return chunk

    def delete_chunk(self, library_id: UUID, document_id: UUID, chunk_id: UUID) -> bool:
        with self.lock_manager.write_lock(f"library_{library_id}"):
            library = self.db.libraries.get(library_id)
            if not library:
                return False

            document = next((doc for doc in library.documents if doc.id == document_id), None)
            if not document:
                return False

            initial_count = len(document.chunks)
            document.chunks = [ch for ch in document.chunks if ch.id != chunk_id]

            if len(document.chunks) < initial_count:
                document.updated_at = datetime.now(timezone.utc)
                library.updated_at = datetime.now(timezone.utc)
                library.is_indexed = False
                self.db.save()
                return True
            return False

    def list_chunks(self, library_id: UUID, document_id: UUID) -> Optional[List[Chunks]]:
        with self.lock_manager.read_lock(f"library_{library_id}"):
            library = self.db.libraries.get(library_id)
            if not library:
                return None

            document = next((doc for doc in library.documents if doc.id == document_id), None)
            if not document:
                return None

            return document.chunks

    def search_chunks(
        self,
        library_id: UUID,
        embedding: List[float],
        k: int = 5,
        filters: Optional[Dict] = None,
        strategy: str = "default",
    ) -> Optional[List[Tuple[Chunks, float]]]:
        with self.lock_manager.read_lock(f"library_{library_id}"):
            library = self.db.libraries.get(library_id)
            if not library or not library.is_indexed:
                return None

            all_chunks = []
            for doc in library.documents:
                all_chunks.extend(doc.chunks)

            self._set_index_strategy(strategy)

            return self.index_strategy.query(embedding, k, filters)
