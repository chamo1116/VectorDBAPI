import json
import os
import uuid
from datetime import datetime
from typing import Dict, Optional

from app.core.models.chunks import Chunks
from app.core.models.documents import Documents
from app.core.models.libraries import Libraries


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class Persistence:
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.libraries: Dict[uuid.UUID, Libraries] = {}
        self.chunks: Dict[uuid.UUID, Dict[uuid.UUID, Chunks]] = {}
        self.documents: Dict[uuid.UUID, Documents] = {}
        self._ensure_storage_dir()
        self.load()

    def _ensure_storage_dir(self) -> None:
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_libraries_file(self) -> str:
        return os.path.join(self.storage_dir, "libraries.json")

    def _get_chunks_file(self, library_id: uuid.UUID) -> str:
        return os.path.join(self.storage_dir, f"chunks_{library_id}.json")

    def _get_documents_file(self) -> str:
        return os.path.join(self.storage_dir, "documents.json")

    def _parse_json_data(self, data: str) -> dict:
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return {}
        return data

    def load(self) -> None:
        # Load libraries
        libraries_file = self._get_libraries_file()
        if os.path.exists(libraries_file):
            with open(libraries_file, "r") as f:
                data = json.load(f)
                self.libraries = {
                    uuid.UUID(lib_id): Libraries.model_validate(self._parse_json_data(lib_data))
                    for lib_id, lib_data in data.items()
                }

        # Load chunks for each library
        for lib_id in self.libraries:
            chunks_file = self._get_chunks_file(lib_id)
            if os.path.exists(chunks_file):
                with open(chunks_file, "r") as f:
                    data = json.load(f)
                    self.chunks[lib_id] = {
                        uuid.UUID(chunk_id): Chunks.model_validate(self._parse_json_data(chunk_data))
                        for chunk_id, chunk_data in data.items()
                    }

        # Load documents
        documents_file = self._get_documents_file()
        if os.path.exists(documents_file):
            with open(documents_file, "r") as f:
                data = json.load(f)
                self.documents = {
                    uuid.UUID(doc_id): Documents.model_validate(self._parse_json_data(doc_data))
                    for doc_id, doc_data in data.items()
                }

    def save(self) -> None:
        """Save all data to storage."""
        # Save libraries
        libraries_file = self._get_libraries_file()
        with open(libraries_file, "w") as f:
            json.dump(
                {str(lib_id): lib.model_dump() for lib_id, lib in self.libraries.items()},
                f,
                indent=2,
                cls=CustomEncoder,
            )

        # Save chunks for each library
        for lib_id, chunks in self.chunks.items():
            chunks_file = self._get_chunks_file(lib_id)
            with open(chunks_file, "w") as f:
                json.dump(
                    {str(chunk_id): chunk.model_dump() for chunk_id, chunk in chunks.items()},
                    f,
                    indent=2,
                    cls=CustomEncoder,
                )

        # Save documents
        documents_file = self._get_documents_file()
        with open(documents_file, "w") as f:
            json.dump(
                {str(doc_id): doc.model_dump() for doc_id, doc in self.documents.items()},
                f,
                indent=2,
                cls=CustomEncoder,
            )

    def get_library(self, library_id: uuid.UUID) -> Optional[Libraries]:
        """Get a library by ID."""
        return self.libraries.get(library_id)

    def get_chunks(self, library_id: uuid.UUID) -> Dict[uuid.UUID, Chunks]:
        """Get all chunks for a library."""
        return self.chunks.get(library_id, {})

    def get_chunk(self, library_id: uuid.UUID, chunk_id: uuid.UUID) -> Optional[Chunks]:
        """Get a specific chunk from a library."""
        return self.chunks.get(library_id, {}).get(chunk_id)

    def get_document(self, document_id: uuid.UUID) -> Optional[Documents]:
        """Get a document by ID."""
        return self.documents.get(document_id)
