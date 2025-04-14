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
    await callback.message.edit_text(
        text="Введите название объявления",
    )
    await state.set_state(ReminderCreateStates.waiting_for_name)


@router.message(StateFilter(ReminderCreateStates.waiting_for_name))
async def fill_name(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите тип объявления",
        reply_markup=ReminderCreationKeyboards.choose_reminder_type,
    )
    await state.set_state(ReminderCreateStates.waiting_for_reminder_type)
    await state.update_data(name=message.text)


@router.callback_query(StateFilter(ReminderCreateStates.waiting_for_reminder_type))
async def choose_reminder_type(callback: CallbackQuery, state: FSMContext):
    if callback.data != "other_reminder_type":
        await callback.message.edit_text(
            text="Выберите время начала напоминания",
            reply_markup=ReminderCreationKeyboards.choose_reminder_start_time,
        )
        await state.set_state(ReminderCreateStates.waiting_for_start_time_choice)
    else:
        await callback.message.edit_text(
            text="Введите свой интервал в формате «1 год 2 месяца 3 дня 4 часа 5 минут»",
            reply_markup=ReminderCreationKeyboards.to_main_menu
        )
        await state.set_state(ReminderCreateStates.waiting_for_custom_interval)
    await state.update_data(reminder_type=callback.data)

@router.message(StateFilter(ReminderCreateStates.waiting_for_custom_interval))
async def choose_reminder_start_time(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите время начала напоминания",
        reply_markup=ReminderCreationKeyboards.choose_reminder_start_time,
    )
    await state.set_state(ReminderCreateStates.waiting_for_start_time_choice)
    await state.update_data(custom_interval=message.text)


@router.callback_query(StateFilter(ReminderCreateStates.waiting_for_start_time_choice))
async def choose_reminder_start_time(callback: CallbackQuery, state: FSMContext):
    if callback.data != "custom_start_time":
        await callback.message.edit_text(
            text="Последний шаг",
            reply_markup=ReminderCreationKeyboards.confirm_reminder_creation
        )
        await state.set_state(ReminderCreateStates.waiting_for_reminder_confirmation)
    else:
        await callback.message.edit_text(
            text="Введите дату начала напоминания в формате «ДД.ММ.ГГГГ ЧЧ:ММ»",
            reply_markup=ReminderCreationKeyboards.to_main_menu
        )
        await state.set_state(ReminderCreateStates.waiting_for_start_date)

@router.callback_query(StateFilter(ReminderCreateStates.waiting_for_reminder_confirmation))
async def confirm_reminder_creation(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        text="Напоминание создано",
        reply_markup=ReminderCreationKeyboards.confirm_reminder_creation
    )
