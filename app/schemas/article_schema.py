from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Article(BaseModel):
    id: int
    brand_id: int
    title: str
    url: str
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None
    summary: Optional[str] = None

    class Config:
        from_attributes = True
