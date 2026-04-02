from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "inventory_management"
    DB_USER: str = "postgres"
    DB_PASSWORD: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8h 

    DB_MIN_CONN: int = 2
    DB_MAX_CONN: int = 10

    class Config:
        env_file = "backend/.env"

settings = Settings()