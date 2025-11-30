from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base
from app.models.association_tables.association_tables import user_favorites
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    logo_url = Column(String(255), nullable=True)
    website = Column(String(255))
    # official_site = Column(String(255))
    tags = Column(ARRAY(String))
    created_at = Column(DateTime, default=datetime.now())
    favorited_by = relationship(
        "User",
        secondary=user_favorites,
        back_populates="favorite_brands"
    )
