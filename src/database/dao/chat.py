from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.dao.base import BaseDAO
from src.database.models.chat import Chat


class ChatDAO(BaseDAO[Chat]):
    def __init__(self, session: AsyncSession):
        super().__init__(Chat, session)

    async def get_by_tg_id(self, tg_id: int) -> Chat:
        result = await self.session.execute(select(Chat).where(Chat.tg_id == tg_id))

        return result.scalar_one()
