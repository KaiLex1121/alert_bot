from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import Redis
from aiogram.types import CallbackQuery, Message

from src.database.dao.holder import HolderDAO
from src.keyboards.reminder_creation import ReminderCreationKeyboards
from src.states.general import ReminderCreateStates

router: Router = Router()

@router.callback_query(F.data == "create_reminder")
async def create_reminder(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Введите название объявления",
    )
    await state.set_state(ReminderCreateStates.waiting_for_name)


@router.message(StateFilter(ReminderCreateStates.waiting_for_name))
async def fill_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        text="Выберите тип объявления",
        reply_markup=ReminderCreationKeyboards.choose_reminder_type,
    )
    await state.set_state(ReminderCreateStates.waiting_for_reminder_type)