from aiogram import Bot
from aiogram.types import BotCommand


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="get_all", description="Все пользователи"),
        BotCommand(command="check_state", description="Проверить FSM"),
        BotCommand(command="cancel_check_state", description="Отменить проверку FSM"),
    ]
    await bot.set_my_commands(commands)
