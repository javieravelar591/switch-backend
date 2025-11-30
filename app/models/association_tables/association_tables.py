from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

user_favorites = Table(
    'user_favorites',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('brand_id', Integer, ForeignKey('brands.id'), primary_key=True)
)
