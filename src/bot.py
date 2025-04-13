import asyncio
import logging
from typing import Union

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, Redis, RedisStorage
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.config.main_config import Config, load_config
from src.database.models.base import create_pool
from src.handlers import (admin, main_menu, reminder_creation, test_handlers,
                          view_created_reminders)
from src.middlewares.config import ConfigMiddleware
from src.middlewares.data_loader import LoadDataMiddleware
from src.middlewares.database import DBMiddleware
from src.middlewares.redis import RedisMiddleware
from src.utils.general import set_commands


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(main_menu.router)
    dp.include_router(reminder_creation.router)
    dp.include_router(view_created_reminders.router)
    dp.include_router(admin.router)
    dp.include_router(test_handlers.router)


def setup_middlewares(
    dp: Dispatcher,
    pool: async_sessionmaker[AsyncSession],
    bot_config: Config,
    redis: Redis
) -> None:
    dp.update.outer_middleware(ConfigMiddleware(bot_config))
    dp.update.outer_middleware(DBMiddleware(pool))
    dp.update.outer_middleware(RedisMiddleware(redis))
    dp.update.outer_middleware(LoadDataMiddleware())


def get_storage(config: Config) -> Union[MemoryStorage, RedisStorage]:

    if config.tg_bot.use_redis:
        storage = RedisStorage.from_url(
            url=config.redis.create_uri(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True)
        )
    else:
        storage = MemoryStorage()

    return storage


logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.level = logging.INFO


async def main() -> None:
    config = load_config('.env')
    storage = get_storage(config=config)
    bot = Bot(config.tg_bot.token)
    dp = Dispatcher(storage=storage)

    setup_handlers(dp)
    setup_middlewares(dp, create_pool(config.db), config, storage.redis)

    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    finally:
        logger.error("Bot has been stopped")
