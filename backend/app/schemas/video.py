from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, field_validator
from core.config import config


class CopyrightVideoPartSchema(BaseModel):
    id: UUID
    video_id: UUID
    url: str
    start: int
    end: int
    created_at: datetime
    updated_at: datetime


class VideoCreateSchema(BaseModel):
    filename: str | None = None
    user_ip: str | None = None
    url: str | None = None


class VideoSchema(BaseModel):
    id: UUID
    filename: str | None = None
    user_ip: str | None = None
    url: str | None = None
    copyright_video_parts: list[CopyrightVideoPartSchema]
    finished: bool


class CopyrightVideoSchema(BaseModel):
    id: UUID
    filename: str | None = None
    user_ip: str | None = None
    url: str | None = None
    finished: bool


class ListVideoResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[VideoSchema]


class AddCopyrightVideoPartSchema(BaseModel):
    video_id: UUID
    url: str
    start: int
    end: int
