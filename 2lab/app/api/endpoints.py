from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut, Token
from app.cruds.user import get_user_by_email, create_user, authenticate_user, create_access_token, get_current_user
from app.db.base import get_db
from app.services.parsing import parse_website_task
import uuid

router = APIRouter()

# Регистрация
@router.post("/sign-up/", response_model=UserOut)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, user.email, user.password)
    token = create_access_token({"sub": new_user.email})
    return {"id": new_user.id, "email": new_user.email, "token": token}

# Вход
@router.post("/login/", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email})
    return {"id": db_user.id, "email": db_user.email, "token": token}

# Информация о текущем пользователе
@router.get("/users/me/", response_model=UserOut)
def get_me(token: str, db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# Парсинг сайта
@router.post("/parse_website/")
def parse_website(data: dict, db: Session = Depends(get_db)):
    url = data.get("url")
    max_depth = data.get("max_depth", 3)
    format = data.get("format", "graphml")
    task_id = str(uuid.uuid4())
    parse_website_task.delay(url, max_depth, format, task_id)
    return {"task_id": task_id}

# Статус парсинга
@router.get("/parse_status/")
def parse_status(task_id: str):
    from celery.result import AsyncResult
    task = AsyncResult(task_id)
    if task.state == "SUCCESS":
        return {"status": "completed", "progress": 100, "result": task.result}
    elif task.state == "PENDING":
        return {"status": "pending", "progress": 0}
    else:
        return {"status": task.state, "progress": 50}