from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dao import ChatDAO, UserDAO, ReminderDAO


@dataclass
class HolderDAO:
    session: AsyncSession
    user: UserDAO = field(init=False)
    chat: ChatDAO = field(init=False)
    reminder: ReminderDAO = field(init=False)

    def __post_init__(self):
        self.user = UserDAO(self.session)
        self.chat = ChatDAO(self.session)
        self.reminder = ReminderDAO(self.session)

    async def commit(self):
        await self.session.commit()
