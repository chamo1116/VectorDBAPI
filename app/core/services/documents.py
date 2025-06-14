from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from app.core.models.documents import Documents
from app.core.services.base_service import BaseService
from app.infrastructure.locking import LockManager
from app.infrastructure.persistence import Persistence


class DocumentsService(BaseService):
    def __init__(self, db: Persistence, lock_manager: LockManager):
        super().__init__(db, lock_manager)

    def create_document(
        self,
        library_id: UUID,
        name: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Optional[Documents]:
        """Create a new document in a library."""
        with self.lock_manager.write_lock("documents"):
            # Check if library exists
            if library_id not in self.db.libraries:
                return None

            document = Documents(
                library_id=library_id,
                name=name,
                metadata=metadata or {},
            )
            self.db.documents[document.id] = document
            self.db.save()
            return document

    def get_document(self, document_id: UUID) -> Optional[Documents]:
        """Retrieve a document by its ID."""
        with self.lock_manager.read_lock("documents"):
            return self.db.documents.get(document_id)

    def update_document(
        self,
        document_id: UUID,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Optional[Documents]:
        """Update an existing document."""
        with self.lock_manager.write_lock("documents"):
            document = self.db.documents.get(document_id)
            if not document:
                return None

            if name is not None:
                document.name = name
            if metadata is not None:
                document.metadata = metadata

            document.updated_at = datetime.now(timezone.utc)
            self.db.documents[document.id] = document
            self.db.save()
            return document

    def delete_document(self, document_id: UUID) -> bool:
        """Delete a document."""
        with self.lock_manager.write_lock("documents"):
            if document_id not in self.db.documents:
                return False

            del self.db.documents[document_id]
            self.db.save()
            return True

    def list_documents(self, library_id: Optional[UUID] = None) -> List[Documents]:
        """List all documents associated to a library"""
        with self.lock_manager.read_lock("documents"):
            documents = list(self.db.documents.values())
            if library_id:
                return [doc for doc in documents if doc.library_id == library_id]
            return documents

    def add_document(
        self, library_id: UUID, name: str, metadata: Optional[Dict[str, str]] = None
    ) -> Optional[Documents]:
        """Add a document to a library."""
        with self.lock_manager.write_lock(f"library_{library_id}"):
            library = self.db.libraries.get(library_id)
            if not library:
                return None

            document = Documents(
                library_id=library_id,
                name=name,
                metadata=metadata or {},
            )
            library.documents.append(document)
            library.updated_at = datetime.now(timezone.utc)
            library.is_indexed = False
            self.db.libraries[library.id] = library
            self.db.save()
            return document
