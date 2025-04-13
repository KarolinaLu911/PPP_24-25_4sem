from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from app.schemas.parser import ParseRequest, ParseResponse, ParseStatusResponse
from app.services.parser import parse_website
from app.services.task_manager import get_task
from app.db.base import get_db
from sqlalchemy.orm import Session
import uuid
import traceback

router = APIRouter()

@router.post("/parse_website", response_model=ParseResponse)
def start_parsing(request: ParseRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        task_id = str(uuid.uuid4())
        # Убедимся, что request.url — это строка
        url = str(request.url) if request.url else None
        if not url:
            raise ValueError("URL cannot be empty")
        print(f"Starting task: {task_id}, URL: {url}, max_depth: {request.max_depth}, format: {request.format}")
        background_tasks.add_task(parse_website, task_id, url, request.max_depth, request.format, db=db)
        return {"task_id": task_id}
    except Exception as e:
        print(f"Error in /parse_website: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/parse_status", response_model=ParseStatusResponse)
def get_parse_status(task_id: str, db: Session = Depends(get_db)):
    print(f"Received request for task_id: {task_id}")
    task = get_task(task_id, db)
    if not task:
        print(f"Task not found: {task_id}")
        raise HTTPException(status_code=404, detail="Задача не найдена")
    print(f"Task status: {task.status}, progress: {task.progress}")
    return {"status": task.status, "progress": task.progress, "result": task.result}