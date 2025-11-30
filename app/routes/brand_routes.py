from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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

@router.get("/", response_model=list[brand_schema.BrandBase])
def get_brands(db: Session = Depends(get_db)):
    brands = db.query(models.brand.Brand).all()
    return brands

@router.post("/", response_model=brand_schema.Brand)
def create_brand(brand: brand_schema.BrandCreate, db: Session = Depends(get_db)):
    db_brand = models.brand.Brand(**brand.dict())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

@router.post("/{brand_id}/favorite")
def favorite_brand(
    brand_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    if brand not in current_user.favorite_brands:
        current_user.favorite_brands.append(brand)
        db.commit()

    return {"message": "Brand favorited"}