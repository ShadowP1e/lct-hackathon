from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_maker
from repositories.video import VideoRepository
from repositories.copyright_video_part import CopyrightVideoPartRepository
from repositories.copyright_video import CopyrightVideoRepository
from repositories.user import UserRepository


class IUnitOfWork(ABC):
    session: AsyncSession
    video: VideoRepository
    copyright_video_part: CopyrightVideoPartRepository
    copyright_video: CopyrightVideoRepository
    user: UserRepository

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()
        self.video = VideoRepository(self.session)
        self.copyright_video_part = CopyrightVideoPartRepository(self.session)
        self.copyright_video = CopyrightVideoRepository(self.session)
        self.user = UserRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
