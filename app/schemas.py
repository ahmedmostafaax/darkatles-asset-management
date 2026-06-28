from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from .models import AssetType, AssetStatus

class AssetCreate(BaseModel):
    type: AssetType
    value: str
    status: AssetStatus = AssetStatus.active
    source: str = "import"
    tags: List[str] = []
    metadata: dict = {}

class AssetUpdate(BaseModel):
    type: Optional[AssetType] = None
    value: Optional[str] = None
    status: Optional[AssetStatus] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None

class AssetResponse(BaseModel):
    id: UUID
    type: AssetType
    value: str
    status: AssetStatus
    first_seen: datetime
    last_seen: datetime
    source: str
    tags: List[str]
    metadata: dict

    class Config:
        from_attributes = True

class RelationshipCreate(BaseModel):
    from_asset_id: UUID
    to_asset_id: UUID
    relationship_type: str

class RelationshipResponse(BaseModel):
    id: UUID
    from_asset_id: UUID
    to_asset_id: UUID
    relationship_type: str
    created_at: datetime

    class Config:
        from_attributes = True