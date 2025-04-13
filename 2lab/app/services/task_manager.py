from typing import Optional
from sqlalchemy.orm import Session
from app.models.task import Task

def create_task(task_id: str, db: Session) -> None:
    db_task = Task(id=task_id, status="pending", progress=0)
    db.add(db_task)
    db.commit()

def update_task(task_id: str, status: str, progress: int, result: Optional[str] = None, db: Session = None) -> None:
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        db_task.status = status
        db_task.progress = progress
        db_task.result = result
        db.commit()

def get_task(task_id: str, db: Session) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()