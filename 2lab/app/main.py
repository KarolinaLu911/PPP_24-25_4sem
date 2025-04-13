import sys
import os
import subprocess
import uvicorn
from fastapi import FastAPI

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.api import auth, parser
    from app.db.base import Base, engine
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    raise

app = FastAPI(title="Website Parser API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(parser.router, prefix="", tags=["parser"])

def run_migrations():
    print("Запуск миграций базы данных с Alembic...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        subprocess.run(["alembic", "upgrade", "head"], cwd=current_dir, check=True)
        print("Миграции успешно выполнены")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении миграций: {e}")
        raise

def run_server():
    print("Запуск сервера FastAPI...")
    try:
        Base.metadata.create_all(bind=engine)
        print("База данных инициализирована")
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
        print("Сервер запущен на http://127.0.0.1:8000")
    except Exception as e:
        print(f"Ошибка при запуске сервера: {e}")
        raise

if __name__ == "__main__":
    run_migrations()
    run_server()