import asyncio

from aiogram import Bot, Dispatcher

from src.config.main_config import load_config
from src.core.setup import setup_full_app, setup_scheduler, setup_storage
from src.database.engine import create_pool


async def main() -> None:
    config = load_config(".env")
    storage = setup_storage(config=config)
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(storage=storage)
    pool = create_pool(config.db)
    scheduler = setup_scheduler(config=config)

    await setup_full_app(
        dp=dp,
        bot=bot,
        pool=pool,
        bot_config=config,
        redis=storage.redis,
        scheduler=scheduler,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        print("Bot has been stopped")
