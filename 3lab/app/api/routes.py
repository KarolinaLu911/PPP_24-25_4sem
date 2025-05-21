from fastapi import APIRouter
from app.celery.tasks import parse_site

router = APIRouter()

@router.post("/parse/")
def start_parsing(user_id: str, url: str, max_depth: int = 3):
    task = parse_site.delay(user_id, url, max_depth)
    return {"task_id": task.id, "status": "STARTED"}
