import asyncio
import websockets
import requests
import json

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/ws"


async def websocket_listener(user_id):
    uri = f"{WS_URL}/{user_id}"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to WebSocket at {uri}")
            while True:
                msg = await websocket.recv()
                print("WebSocket:", json.loads(msg))
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"WebSocket connection closed: {e}")
    except Exception as e:
        print(f"WebSocket error: {e}")


def start_task(user_id, url, depth):
    try:
        response = requests.post(f"{BASE_URL}/api/v1/parse/", json={
            "url": url,
            "max_depth": depth,
            "user_id": user_id  # убедись, что backend ожидает это поле
        })
        response.raise_for_status()
        print("Task started:", response.json())
    except requests.RequestException as e:
        print(f"Failed to start task: {e}")


async def main():
    user_id = 1# input("Enter user ID: ")
    url = input("Enter URL: ")
    depth = int(input("Enter max depth: "))

    # Запускаем прослушку WebSocket параллельно
    listener_task = asyncio.create_task(websocket_listener(236))

    # Стартуем задачу парсинга
    start_task(user_id, url, depth)

    # Ждём завершения listener'а (если когда-нибудь завершится)
    await listener_task


if __name__ == "__main__":
    asyncio.run(main())
