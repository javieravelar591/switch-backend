from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User as UserModel
from app.schemas.user_schema import UserCreate, User, UserLogin, Token
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_db,
)

router = APIRouter(prefix="/user", tags=["users"])

@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == user.email).first()
    print(existing)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_password = hash_password(user.password)
    print(hashed_password)
    db_user = UserModel(email=user.email, username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    print(db_user.id, db_user.email)
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token}

@router.get("/me", response_model=User)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id: int}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/favorites")
def get_user_favorites(current_user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    return current_user.favorites_brands
