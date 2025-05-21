from app.cruds.user import create_user as crud_create_user
from app.schemas.user import UserCreate
from app.db.session import SessionLocal

def create_user(user: UserCreate):
    db = SessionLocal()
    db_user = crud_create_user(db=db, user=user)
    db.close()
    return db_user
