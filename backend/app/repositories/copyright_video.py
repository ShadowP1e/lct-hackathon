from repositories.base import SQLAlchemyRepository
from models import CopyrightVideo


class CopyrightVideoRepository(SQLAlchemyRepository):
    model = CopyrightVideo
