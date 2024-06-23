import os
from datetime import timedelta
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    # base
    PROJECT_NAME: str = "API"
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    APP_HOST: str = '0.0.0.0'
    APP_PORT: int = 8000
    APP_DOMAIN: str = os.getenv('APP_DOMAIN')

    SECRET_KEY = os.getenv("SECRET")
    # database
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_PORT = os.getenv("POSTGRES_PORT")
    DB_NAME = os.getenv("POSTGRES_DB")

    DATABASE_URI = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    # DATABASE_URI = f"sqlite+aiosqlite:///{PROJECT_ROOT}/db.db"
    TEST_DATABASE_URI = f"sqlite+aiosqlite:///{PROJECT_ROOT}/test_db.db"

    # auth
    JWT_SECRET = os.getenv("SECRET")
    JWT_ACCESS_EXPIRE: timedelta = timedelta(minutes=60)
    JWT_REFRESH_EXPIRE: timedelta = timedelta(days=180)
    COOKIE_SECURE: bool = False

    # minio s3
    MINIO_DOMAIN = os.getenv("MINIO_DOMAIN")
    MINIO_PORT = os.getenv("MINIO_PORT")
    MINIO_USER = os.getenv("MINIO_USER")
    MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")

    # rabbitmq
    RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_DEFAULT_PASS")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")

    # default user
    DEFAULT_USER_EMAIL = os.getenv("DEFAULT_USER_EMAIL", "admin@admin.ru")
    DEFAULT_USER_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD", "admin")


@dataclass(frozen=True)
class ProdConfig(Config):
    COOKIE_DOMAIN: str = "90.156.227.135"
    CORS_ORIGINS: tuple[str] = ("http://90.156.227.135", "http://90.156.227.135:8000", "http://90.156.227.135:8080")
    SHOW_DOCS: bool = False


@dataclass(frozen=True)
class DevConfig(Config):
    COOKIE_DOMAIN: str = "localhost"
    CORS_ORIGINS: tuple[str] = (
        "http://127.0.0.1:8000", "http://localhost:8000", "http://127.0.0.1", "http://localhost",
        "http://127.0.0.1:8080", "http://localhost:8080",
    )
    SHOW_DOCS: bool = True


def get_config():
    env = os.getenv("ENV", "dev")
    config_type = {
        "dev": DevConfig(),
        "prod": ProdConfig(),
    }
    return config_type[env]


config = get_config()
