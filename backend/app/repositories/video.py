from repositories.base import SQLAlchemyRepository
from models import Video


class VideoRepository(SQLAlchemyRepository):
    model = Video
