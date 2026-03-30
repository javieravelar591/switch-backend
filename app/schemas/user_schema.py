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
    style_profile: str | None = None
    favorite_brands: list[BrandBase] = []

    class Config:
        from_attributes = True

# User Style quiz
class QuizAnswers(BaseModel):
    aesthetics: list[str] = []
    budget: str = ""
    values: list[str] = []

    @field_validator("aesthetics", "values")
    @classmethod
    def limit_list(cls, v: list[str]) -> list[str]:
        if len(v) > 10:
            raise ValueError("Too many selections")
        return [s[:100] for s in v]

    @field_validator("budget")
    @classmethod
    def limit_budget(cls, v: str) -> str:
        return v[:100]
