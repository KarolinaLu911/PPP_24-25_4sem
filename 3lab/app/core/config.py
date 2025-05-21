from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI Project"
    database_url: str = "sqlite:///./test.db"
    secret_key: str = "mysecretkey"
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()
