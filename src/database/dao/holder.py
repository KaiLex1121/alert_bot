from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dao.base import BaseDAO
from src.database.dao.chat import ChatDAO
from src.database.dao.reminder import ReminderDAO
from src.database.dao.user import UserDAO
from src.database.models.base import Base


@dataclass
class HolderDAO:
    session: AsyncSession
    base: BaseDAO = field(init=False)
    user: UserDAO = field(init=False)
    chat: ChatDAO = field(init=False)
    reminder: ReminderDAO = field(init=False)

    def __post_init__(self):
        self.user = UserDAO(self.session)
        self.chat = ChatDAO(self.session)
        self.base = BaseDAO(Base, self.session)
        self.reminder = ReminderDAO(self.session)

    async def commit(self):
        await self.session.commit()
