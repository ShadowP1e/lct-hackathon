import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    # rabbitmq
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")

    # minio s3
    MINIO_DOMAIN = os.getenv("MINIO_DOMAIN")
    MINIO_PORT = os.getenv("MINIO_PORT")
    MINIO_USER = os.getenv("MINIO_USER")
    MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")


config = Config()
