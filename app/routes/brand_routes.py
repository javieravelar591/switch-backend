from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from app.schemas import brand_schema

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