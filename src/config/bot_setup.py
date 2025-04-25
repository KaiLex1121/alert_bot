import os
from typing import Union

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, Redis, RedisStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.config.main_config import Config

from src.handlers import (
    admin,
    main_menu,
    reminder_creation,
    test_handlers,
    view_created_reminders,
)
from src.middlewares.config import ConfigMiddleware
from src.middlewares.data_loader import LoadDataMiddleware
from src.middlewares.database import DBMiddleware
from src.middlewares.redis import RedisMiddleware
from src.middlewares.scheduler import SchedulerMiddleware
from src.services.scheduler import SchedulerService


def setup_scheduler(config: Config) -> AsyncIOScheduler:

    redis_jobstore_config = {
        "password": config.redis.password,
        "host": config.redis.host,
        "port": config.redis.port,
        "db": config.redis.database,
    }

    jobstores = {"default": RedisJobStore(**redis_jobstore_config)}

    scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="Europe/Moscow")

    return scheduler


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
    redis: Redis,
    scheduler_service: SchedulerService,
) -> None:
    dp.update.outer_middleware(ConfigMiddleware(bot_config))
    dp.update.outer_middleware(DBMiddleware(pool))
    dp.update.outer_middleware(RedisMiddleware(redis))
    dp.update.outer_middleware(LoadDataMiddleware())
    dp.update.outer_middleware(SchedulerMiddleware(scheduler_service))


def setup_storage(config: Config) -> Union[MemoryStorage, RedisStorage]:

    if config.tg_bot.use_redis:
        storage = RedisStorage.from_url(
            url=config.redis.create_uri(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        storage = MemoryStorage()

    return storage
