from pydantic import BaseModel
from typing import Optional

class BrandBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    # official_site: Optional[str] = None
    tags: list[str] = []
    region: Optional[str] = None
    country: Optional[str] = None

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int
    popular: bool = False

    class Config:
        from_attributes = True