from pydantic import BaseModel, EmailStr
from app.schemas.brand_schema import BrandBase

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class User(UserBase):
    id: int
    email: str
    username: str
    favorite_brands: list[BrandBase] = []

    class Config:
        from_attributes = True
