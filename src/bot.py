import asyncio
import datetime
import os
import time

from aiogram import Bot, Dispatcher
from pytz import timezone

from src.config.bot_setup import (
    setup_handlers,
    setup_middlewares,
    setup_scheduler,
    setup_services,
    setup_storage,
)
from src.config.main_config import load_config
from src.context import AppContext
from src.database.engine import create_pool
from src.services.scheduler import SchedulerService
from src.utils.general import set_commands
from src.utils.setup_logging import setup_logging


async def main() -> None:
    config = load_config(".env")
    storage = setup_storage(config=config)
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(storage=storage)
    scheduler = setup_scheduler(config=config)

    setup_handlers(dp)
    setup_middlewares(
        dp=dp, pool=create_pool(config.db), bot_config=config, redis=storage.redis
    )
    setup_logging()
    setup_services(dp=dp, scheduler=scheduler)

    os.environ["TZ"] = "Europe/Moscow"
    time.tzset()
    AppContext.set_bot(bot)
    scheduler.start()

    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        print("Bot has been stopped")
