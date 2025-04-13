from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    REDIS_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Проверяем, существует ли файл .env
if not os.path.exists(".env"):
    raise FileNotFoundError("Файл .env не найден в текущей директории")

settings = Settings()