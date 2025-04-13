import subprocess
import uvicorn
import os
from fastapi import FastAPI
from app.api import auth, parser
from app.db.base import Base, engine

app = FastAPI(title="Website Parser API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(parser.router, prefix="", tags=["parser"])

def run_migrations():
    print("Запуск миграций базы данных с Alembic...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(["alembic", "upgrade", "head"], cwd=current_dir, check=True)

def run_server():
    print("Запуск сервера FastAPI...")
    Base.metadata.create_all(bind=engine)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)  # Убрали workers=2

if __name__ == "__main__":
    run_migrations()
    run_server()