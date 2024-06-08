from repositories.base import SQLAlchemyRepository
from models import CopyrightVideoPart


class CopyrightVideoPartRepository(SQLAlchemyRepository):
    model = CopyrightVideoPart
