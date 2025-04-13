from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse, UserMeResponse
from app.cruds.user import create_user, get_user_by_email, authenticate_user
from app.core.auth import create_access_token, get_current_user
from app.db.base import get_db
from app.models.user import User

router = APIRouter()

@router.post("/register/", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    new_user = create_user(db, user.email, user.password)
    token = create_access_token({"sub": new_user.email})
    return {"id": new_user.id, "email": new_user.email, "token": token}

@router.post("/login/", response_model=UserResponse)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email})
    return {"id": db_user.id, "email": db_user.email, "token": token}

@router.get("/users/me/", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}