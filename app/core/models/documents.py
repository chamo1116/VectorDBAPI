from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.models.chunks import Chunks


class DocumentCreate(BaseModel):
    name: str
    metadata: Optional[dict] = {}


class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    metadata: Optional[dict] = None


class Documents(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    chunks: List[Chunks] = Field(default_factory=list)
    library_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, str] = Field(default_factory=dict)

    model_config = {
        "json_encoders": {
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda uid: str(uid),
        }
    }
