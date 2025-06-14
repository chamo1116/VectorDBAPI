from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class Chunks(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    text: str
    embedding: Optional[List[float]]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, str] = Field(default_factory=dict)

    @field_validator("embedding")
    def validate_embedding(cls, v):
        if not v:
            raise ValueError("Embedding cannot be empty")
        return v

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda uid: str(uid),
        }
