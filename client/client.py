# client/client.py
from typing import Dict, List, Optional
from uuid import UUID

import requests

from client.exceptions import VectorAPIError


class VectorDBClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def create_library(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        response = requests.post(
            f"{self.base_url}/libraries/",
            json={"name": name, "description": description, "metadata": metadata or {}},
        )
        if response.status_code != 200:
            raise VectorAPIError(response.status_code, response.text)
        return response.json()

    def get_library(self, library_id: UUID) -> Dict:
        response = requests.get(f"{self.base_url}/libraries/{str(library_id)}")
        if response.status_code != 200:
            raise VectorAPIError(response.status_code, response.text)
        return response.json()

    def add_document(self, library_id: UUID, name: str, metadata: Optional[Dict] = None) -> Dict:
        response = requests.post(
            f"{self.base_url}/libraries/{str(library_id)}/documents/",
            json={"name": name, "metadata": metadata or {}},
        )
        if response.status_code != 200:
            raise VectorAPIError(response.status_code, response.text)
        return response.json()

    def add_chunk(
        self,
        library_id: UUID,
        document_id: UUID,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict] = None,
    ) -> Dict:
        response = requests.post(
            f"{self.base_url}/libraries/{str(library_id)}/documents/{str(document_id)}/chunks/",
            json={"text": text, "embedding": embedding, "metadata": metadata or {}},
        )
        if response.status_code != 200:
            raise VectorAPIError(response.status_code, response.text)
        return response.json()

    def index_library(self, library_id: UUID) -> bool:
        response = requests.post(f"{self.base_url}/libraries/{str(library_id)}/index")
        if response.status_code != 200:
            raise VectorAPIError(response.status_code, response.text)
        return response.json().get("success", False)

    def search(
        self,
        library_id: UUID,
        embedding: List[float],
        k: int = 5,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        response = requests.post(
            f"{self.base_url}/libraries/{str(library_id)}/search",
            json={"embedding": embedding, "k": k, "filters": filters or {}},
        )
        if response.status_code != 200:
            raise VectorAPIError(response.status_code, response.text)
        return response.json()
