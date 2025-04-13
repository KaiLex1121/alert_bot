from aiogram import Bot, exceptions
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.states.general_states import MainStates
from src.keyboards.main_menu import MainMenuKeyboards


async def render_main_menu(
    message: Message,
    state: FSMContext,
    message_to_delete: int,
    bot: Bot
):
    text = "Выбери нужное"
    try:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message_to_delete
        )
    except exceptions.TelegramBadRequest:
        await message.answer(
        text=text,
        reply_markup=MainMenuKeyboards.main_window
    )

    await state.set_state(MainStates.MAIN_DIALOG)