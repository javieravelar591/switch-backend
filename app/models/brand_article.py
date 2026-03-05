from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class BrandArticle(Base):
    __tablename__ = "brand_articles"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    source = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)
    image_url = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    fetched_at = Column(DateTime, default=func.now())

    brand = relationship("Brand", back_populates="articles")
