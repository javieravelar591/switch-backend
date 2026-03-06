from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
from app.database import SessionLocal
from app import models
from app.schemas import brand_schema, article_schema
from app.models.brand_article import BrandArticle
from app.models.association_tables.association_tables import user_favorites
from app.services.news_fetcher import fetch_all
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/brands", tags=["brands"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

POPULAR_THRESHOLD = 3

@router.get("", response_model=list[brand_schema.Brand])
def get_brands(
    skip: int = Query(default=0, ge=0, le=10000),
    limit: int = Query(default=10, ge=1, le=100),
    category: Optional[str] = Query(default=None, max_length=50),
    region: Optional[str] = Query(default=None, max_length=50),
    search: Optional[str] = Query(default=None, max_length=100),
    sort: Optional[str] = Query(default=None, pattern="^(name|popular|newest)$"),
    db: Session = Depends(get_db),
):
    fav_sq = (
        db.query(user_favorites.c.brand_id, func.count().label("cnt"))
        .group_by(user_favorites.c.brand_id)
        .subquery()
    )
    fav_col = func.coalesce(fav_sq.c.cnt, 0)

    query = (
        db.query(models.brand.Brand, fav_col.label("fav_count"))
        .outerjoin(fav_sq, models.brand.Brand.id == fav_sq.c.brand_id)
    )
    if category:
        query = query.filter(models.brand.Brand.category == category)
    if region:
        query = query.filter(models.brand.Brand.region == region)
    if search:
        query = query.filter(models.brand.Brand.name.ilike(f"%{search}%"))
    if sort == "name":
        query = query.order_by(models.brand.Brand.name.asc())
    elif sort == "popular":
        query = query.order_by(fav_col.desc())
    elif sort == "newest":
        query = query.order_by(models.brand.Brand.created_at.desc())

    rows = query.offset(skip).limit(limit).all()
    return [
        {
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "category": b.category,
            "logo_url": b.logo_url,
            "website": b.website,
            "tags": b.tags or [],
            "region": b.region,
            "country": b.country,
            "popular": fav_count >= POPULAR_THRESHOLD,
        }
        for b, fav_count in rows
    ]

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


@router.get("/{brand_id}", response_model=brand_schema.Brand)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(models.brand.Brand).filter(models.brand.Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


ARTICLE_CACHE_HOURS = 6

@router.get("/{brand_id}/articles", response_model=list[article_schema.Article])
def get_brand_articles(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(models.brand.Brand).filter(models.brand.Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Return cached articles if fetched within the last ARTICLE_CACHE_HOURS
    cutoff = datetime.utcnow() - timedelta(hours=ARTICLE_CACHE_HOURS)
    cached = (
        db.query(BrandArticle)
        .filter(BrandArticle.brand_id == brand_id, BrandArticle.fetched_at >= cutoff)
        .order_by(BrandArticle.published_at.desc())
        .all()
    )
    if cached:
        return cached

    # Fetch fresh articles
    raw_articles = fetch_all(brand.name, brand.category)

    for a in raw_articles:
        if not a.get("url") or not a.get("title"):
            continue
        # Upsert by URL — skip if already stored
        exists = db.query(BrandArticle).filter(BrandArticle.url == a["url"]).first()
        if not exists:
            db.add(BrandArticle(
                brand_id=brand_id,
                title=a["title"],
                url=a["url"],
                source=a.get("source"),
                published_at=a.get("published_at"),
                image_url=a.get("image_url"),
                summary=a.get("summary"),
            ))

    db.commit()

    return (
        db.query(BrandArticle)
        .filter(BrandArticle.brand_id == brand_id)
        .order_by(BrandArticle.published_at.desc())
        .limit(20)
        .all()
    )


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
