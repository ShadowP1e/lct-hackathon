import datetime as dt
from uuid import UUID, uuid4

from sqlalchemy import String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from utils.time import get_utc


class CopyrightVideo(Base):
    __tablename__ = 'copyright_videos'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    filename: Mapped[str] = mapped_column(String(250), nullable=True)
    user_ip: Mapped[str] = mapped_column(String(60), nullable=True)
    url: Mapped[str] = mapped_column(String(250), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(type_=TIMESTAMP(timezone=True), default=get_utc)
    updated_at: Mapped[dt.datetime] = mapped_column(type_=TIMESTAMP(timezone=True), default=get_utc, onupdate=get_utc)

    finished: Mapped[bool] = mapped_column(default=False)
