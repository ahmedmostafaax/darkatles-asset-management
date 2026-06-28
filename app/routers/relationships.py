from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import os

from ..database import get_db
from ..models import Relationship, Asset
from ..schemas import RelationshipCreate, RelationshipResponse, AssetResponse

router = APIRouter(prefix="/relationships", tags=["relationships"])

API_KEY = os.getenv("API_KEY", "secret-key")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@router.post("/", response_model=RelationshipResponse)
def create_relationship(
    rel: RelationshipCreate,
    db: Session = Depends(get_db),
    x_api_key: str = Header(...)
):
    verify_api_key(x_api_key)
    from_asset = db.query(Asset).filter(Asset.id == rel.from_asset_id).first()
    to_asset = db.query(Asset).filter(Asset.id == rel.to_asset_id).first()
    if not from_asset or not to_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    new_rel = Relationship(
        from_asset_id=rel.from_asset_id,
        to_asset_id=rel.to_asset_id,
        relationship_type=rel.relationship_type
    )
    db.add(new_rel)
    db.commit()
    db.refresh(new_rel)
    return new_rel

@router.get("/asset/{asset_id}")
def get_asset_with_relationships(asset_id: UUID, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    rels_from = asset.relationships_from
    rels_to = asset.relationships_to
    return {
        "asset": asset,
        "relationships": {
            "outgoing": [
                {
                    "id": r.id,
                    "to_asset_id": r.to_asset_id,
                    "relationship_type": r.relationship_type
                } for r in rels_from
            ],
            "incoming": [
                {
                    "id": r.id,
                    "from_asset_id": r.from_asset_id,
                    "relationship_type": r.relationship_type
                } for r in rels_to
            ]
        }
    }