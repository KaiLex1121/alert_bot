import asyncio
import logging
from typing import Union

from aiogram import Bot, exceptions
from aiogram.types import InlineKeyboardMarkup


async def send_message_safely(
    bot: Bot,
    user_id: Union[int, str],
    text: str,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup = None,
) -> bool:
    try:
        await bot.send_message(
            user_id,
            text,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
        )
    except exceptions.TelegramBadRequest as err:
        logging.error(f"Telegram server says: {err.message}")
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_message_safely(
            bot, user_id, text, disable_notification, reply_markup
        )  # Recursive call
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def broadcast(
    bot: Bot,
    users: list[Union[str, int]],
    text: str,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup = None,
) -> int:
    count = 0
    try:
        for tpl in users:
            user_id = tpl[0].tg_id
            if await send_message_safely(
                bot, user_id, text, disable_notification, reply_markup
            ):
                count += 1
            await asyncio.sleep(
                0.05
            )  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logging.info(f"{count} messages successful sent.")

    return count
