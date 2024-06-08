import datetime as dt
from uuid import UUID, uuid4
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from utils.time import get_utc

if TYPE_CHECKING:
    from models import Video


class CopyrightVideoPart(Base):
    __tablename__ = 'copyright_video_parts'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    video_id: Mapped[UUID] = mapped_column(ForeignKey('videos.id'))
    video: Mapped["Video"] = relationship("Video", back_populates="copyright_video_parts")

    url: Mapped[str] = mapped_column()
    start: Mapped[int] = mapped_column()
    end: Mapped[int] = mapped_column()

    created_at: Mapped[dt.datetime] = mapped_column(type_=TIMESTAMP(timezone=True), default=get_utc)
    updated_at: Mapped[dt.datetime] = mapped_column(type_=TIMESTAMP(timezone=True), default=get_utc, onupdate=get_utc)
