from typing import Any

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.keyboards.main_menu import MainMenuKeyboards
from src.states.general import MainStates

router: Router = Router()


@router.callback_query(F.data == "to_main_menu")
async def render_main_menu(callback: CallbackQuery, bot: Bot, state: FSMContext):
    text = "Вы вернулись в главное меню.\nВыберите действие"
    try:
        await callback.message.edit_text(
            text=text, reply_markup=MainMenuKeyboards.main_window
        )
    except TelegramBadRequest:
        await callback.message.answer(
            text=text, reply_markup=MainMenuKeyboards.main_window
        )
    await state.clear()
    await state.set_state(MainStates.MAIN_DIALOG)


@router.message(Command("start"))
async def get_started(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    await message.answer(
        text="Выберите действие", reply_markup=MainMenuKeyboards.main_window
    )
    await state.set_state(MainStates.MAIN_DIALOG)
