from app.models import Users
from app.repository.base import BaseRepository, SessionFactory


class UserRepository(BaseRepository):
    def __init__(self, session: SessionFactory):
        super().__init__(session=session, model=Users)
