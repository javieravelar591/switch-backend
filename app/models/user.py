from sqlalchemy import Column, Integer, String
from app.database import Base
from app.models.association_tables.association_tables import user_favorites
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    favorite_brands = relationship(
        "Brand",
        secondary=user_favorites,
        back_populates="favorited_by",
        lazy="joined"
    )