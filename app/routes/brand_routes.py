from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app import models
from app.schemas import brand_schema
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/brands", tags=["brands"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[brand_schema.Brand])
def get_brands(
    skip: int = Query(default=0, ge=0, le=10000),
    limit: int = Query(default=10, ge=1, le=100),
    category: Optional[str] = Query(default=None, max_length=50),
    db: Session = Depends(get_db),
):
    query = db.query(models.brand.Brand)
    if category:
        query = query.filter(models.brand.Brand.category == category)
    return query.offset(skip).limit(limit).all()

@router.get("/recommendations", response_model=list[brand_schema.Brand])
def get_recommendations(
    limit: int = Query(default=12, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    favorited_ids = {b.id for b in current_user.favorite_brands}
    if not favorited_ids:
        return []

    tag_weights: dict[str, int] = {}
    for brand in current_user.favorite_brands:
        for tag in (brand.tags or []):
            tag_weights[tag] = tag_weights.get(tag, 0) + 1

    candidates = db.query(models.brand.Brand).filter(
        models.brand.Brand.id.notin_(favorited_ids)
    ).all()

    scored = []
    for brand in candidates:
        score = sum(tag_weights.get(t, 0) for t in (brand.tags or []))
        if score > 0:
            scored.append((score, brand))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [b for _, b in scored[:limit]]


@router.post("/{brand_id}/favorite")
def toggle_favorite(
    brand_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    brand = db.query(models.brand.Brand).filter(models.brand.Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    if brand in user.favorite_brands:
        user.favorite_brands.remove(brand)
        db.commit()
        return {"favorited": False}
    else:
        user.favorite_brands.append(brand)
        db.commit()
        return {"favorited": True}
