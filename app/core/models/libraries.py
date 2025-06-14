from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.models.documents import Documents


class Libraries(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    documents: List[Documents] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, str] = Field(default_factory=dict)
    is_indexed: bool = Field(default=False)

    model_config = {
        "json_encoders": {
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda uid: str(uid),
        }
    }
