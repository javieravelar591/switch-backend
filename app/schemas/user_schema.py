from pydantic import BaseModel, EmailStr, field_validator
from app.schemas.brand_schema import BrandBase

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

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
