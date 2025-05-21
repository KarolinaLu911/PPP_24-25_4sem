from fastapi import WebSocket, WebSocketDisconnect
from app.celery.tasks import parse_site
from app.celery.tasks import send_progress_to_ws
import asyncio


class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        self.active_connections[task_id] = websocket
        print(f"WebSocket connected for task {task_id}")  # Логируем успешное подключение

    async def disconnect(self, websocket: WebSocket, task_id: str):
        del self.active_connections[task_id]
        await websocket.close()
        print(f"WebSocket disconnected for task {task_id}")  # Логируем отключение

    async def send_message(self, task_id: str, message: dict):
        """Отправляем сообщение через WebSocket по task_id."""
        websocket = self.active_connections.get(task_id)
        if websocket:
            await websocket.send_json(message)


manager = WebSocketConnectionManager()


async def handle_task_progress(task_id: str):
    while True:
        status = parse_site.AsyncResult(task_id)
        print(f"Checking status for task {task_id}: {status.state}")  # Логируем состояние задачи


        if status.state == 'STARTED' or status.state == 'PROGRESS':
            if status.info:
                progress_data = status.info
                print(f"Sending progress: {progress_data}")  # Логируем отправку прогресса
                await manager.send_message(task_id, {
                    "status": "PROGRESS",
                    "task_id": task_id,
                    "progress": progress_data['progress'],
                    "current_url": progress_data.get('current_url'),
                    "pages_parsed": progress_data.get('pages_parsed', 0),
                    "total_pages": progress_data.get('total_pages', 0),
                    "links_found": progress_data.get('links_found', 0)
                })
        elif status.state == 'SUCCESS':
            result = status.result
            print(f"Task {task_id} completed with result: {result}")  # Логируем завершение задачи
            await manager.send_message(task_id, {
                "status": "COMPLETED",
                "task_id": task_id,
                "total_pages": result.get('total_pages', 0),
                "total_links": result.get('total_links', 0),
                "elapsed_time": result.get('elapsed_time', 'N/A'),
                "result": result.get('result', 'N/A')
            })
            break


        elif status.state == 'FAILURE':
            print(f"Task {task_id} failed with error: {status.result}")  # Логируем ошибку
            await manager.send_message(task_id, {
                "status": "FAILED",
                "task_id": task_id,
                "error": status.result
            })
            break

        await asyncio.sleep(1)


# Эндпоинт WebSocket для подключения клиента
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await manager.connect(websocket, task_id)
    try:
        asyncio.create_task(handle_task_progress(task_id))

        while True:
            message = await websocket.receive_text()
            print(f"Received message from task {task_id}: {message}")
    except WebSocketDisconnect:
        await manager.disconnect(websocket, task_id)
