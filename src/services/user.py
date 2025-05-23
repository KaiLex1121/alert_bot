from src import dto
from src.database.dao.user import UserDAO


async def upsert_user(user: dto.User, user_dao: UserDAO) -> dto.User:
    saved_user = await user_dao.upsert_user(user)
    await user_dao.commit()
    return saved_user
