from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    email: str
    username: str
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True
