import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi import Request
from pydantic import BaseModel
from app.celery.tasks import parse_site
from uuid import uuid4
from typing import Dict
import asyncio
from app.services.auth import create_user as cr_user_func
from app.schemas.user import UserCreate
import redis.asyncio as redis
import json
import redis.asyncio as aioredis

router = APIRouter()
logger = logging.getLogger(__name__)
# Хранилище подключений: task_id -> WebSocket
connections: Dict[str, WebSocket] = {}


class ParseRequest(BaseModel):
    url: str
    max_depth: int

class UserRequest(BaseModel):
    name: str
    age: int


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()

    # подключаемся к Redis
    redis = aioredis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"task_channel:{236}")

    try:
        # слушаем канал
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                # сразу шлём клиенту
                await websocket.send_json(data)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {236}")
    finally:
        # чистим ресурсы
        await pubsub.unsubscribe(f"task_channel:{236}")
        await pubsub.close()
        await redis.close()
# @router.websocket("/ws/{task_id}")
# async def websocket_endpoint(websocket: WebSocket, task_id: str):
#     await websocket.accept()
#     try:
#         while True:
#             # ждём следующее текстовое сообщение
#             message = await websocket.receive_text()
#             # выводим только когда что-то пришло
#             print(f"[{task_id}] Received:", message)
#     except WebSocketDisconnect:
#         print(f"WebSocket disconnected: {task_id}")
# POST /parse/
@router.post("/parse/")
async def start_parsing(request: ParseRequest, websocket: WebSocket = None):
    try:
        async_result = parse_site(
            url=request.url,
            max_depth=request.max_depth,
            #connections=connections  # Ваш словарь с WebSocket соединениями
        )
        # parse_site(
        #     url=request.url,
        #     max_depth=request.max_depth,
        # )
        return {"task_id": "236"}
        #return {"task_id": async_result.id}

    except Exception as e:
        logger.error(f"Failed to start task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_user/")
async def create_user(request: UserRequest):
    user_data = UserCreate(name=request.name, age=request.age)
    cr_user_func(user=user_data)
    return {"status": "OK"}


