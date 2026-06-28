from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import os

from ..database import get_db
from ..models import Asset, AssetStatus, AssetType
from ..schemas import AssetCreate, AssetUpdate, AssetResponse

router = APIRouter(prefix="/assets", tags=["assets"])

API_KEY = os.getenv("API_KEY", "secret-key")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@router.get("/", response_model=List[AssetResponse])
def list_assets(
    type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    tag: Optional[str] = None,
    value_contains: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Asset)
    if type:
        query = query.filter(Asset.type == type)
    if status:
        query = query.filter(Asset.status == status)
    if value_contains:
        query = query.filter(Asset.value.contains(value_contains))
    if tag:
        query = query.filter(Asset.tags.contains([tag]))
    return query.offset(skip).limit(limit).all()

@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: UUID, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.post("/", response_model=AssetResponse)
def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db),
    x_api_key: str = Header(...)
):
    verify_api_key(x_api_key)
    existing = db.query(Asset).filter(
        Asset.type == asset.type,
        Asset.value == asset.value
    ).first()
    if existing:
        existing.last_seen = datetime.utcnow()
        existing.tags = list(set(existing.tags + asset.tags))
        existing.metadata_ = {**existing.metadata_, **asset.metadata}
        if existing.status == AssetStatus.stale:
            existing.status = AssetStatus.active
        db.commit()
        db.refresh(existing)
        return existing
    new_asset = Asset(
        type=asset.type,
        value=asset.value,
        status=asset.status,
        source=asset.source,
        tags=asset.tags,
        metadata_=asset.metadata
    )
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    return new_asset

@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: UUID,
    asset: AssetUpdate,
    db: Session = Depends(get_db),
    x_api_key: str = Header(...)
):
    verify_api_key(x_api_key)
    existing = db.query(Asset).filter(Asset.id == asset_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.type: existing.type = asset.type
    if asset.value: existing.value = asset.value
    if asset.status: existing.status = asset.status
    if asset.source: existing.source = asset.source
    if asset.tags: existing.tags = asset.tags
    if asset.metadata: existing.metadata_ = asset.metadata
    existing.last_seen = datetime.utcnow()
    db.commit()
    db.refresh(existing)
    return existing

@router.delete("/{asset_id}")
def delete_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    x_api_key: str = Header(...)
):
    verify_api_key(x_api_key)
    existing = db.query(Asset).filter(Asset.id == asset_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(existing)
    db.commit()
    return {"message": "Asset deleted successfully"}

@router.post("/bulk-import", response_model=dict)
def bulk_import(
    assets: List[AssetCreate],
    db: Session = Depends(get_db),
    x_api_key: str = Header(...)
):
    verify_api_key(x_api_key)
    created, updated, failed = 0, 0, 0
    for asset_data in assets:
        try:
            existing = db.query(Asset).filter(
                Asset.type == asset_data.type,
                Asset.value == asset_data.value
            ).first()
            if existing:
                existing.last_seen = datetime.utcnow()
                existing.tags = list(set(existing.tags + asset_data.tags))
                existing.metadata_ = {**existing.metadata_, **asset_data.metadata}
                if existing.status == AssetStatus.stale:
                    existing.status = AssetStatus.active
                updated += 1
            else:
                new_asset = Asset(
                    type=asset_data.type,
                    value=asset_data.value,
                    status=asset_data.status,
                    source=asset_data.source,
                    tags=asset_data.tags,
                    metadata_=asset_data.metadata
                )
                db.add(new_asset)
                created += 1
        except Exception:
            failed += 1
    db.commit()
    return {"created": created, "updated": updated, "failed": failed}

@router.patch("/{asset_id}/stale")
def mark_stale(
    asset_id: UUID,
    db: Session = Depends(get_db),
    x_api_key: str = Header(...)
):
    verify_api_key(x_api_key)
    existing = db.query(Asset).filter(Asset.id == asset_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Asset not found")
    existing.status = AssetStatus.stale
    db.commit()
    return {"message": "Asset marked as stale"}