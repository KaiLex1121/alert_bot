from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import Redis
from aiogram.types import CallbackQuery, Message

from src.database.dao import HolderDAO
from src.keyboards.reminder_creation import ReminderCreationKeyboards
from src.states.general import ReminderCreateStates

router: Router = Router()


@router.callback_query(F.data == "create_reminder")
async def fill_reminder_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Введите название объявления",
    )
    await state.clear()
    await state.set_state(ReminderCreateStates.waiting_for_name)


@router.message(StateFilter(ReminderCreateStates.waiting_for_name))
async def choose_reminder_type(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        text="Выберите тип объявления",
        reply_markup=ReminderCreationKeyboards.choose_reminder_type,
    )
    await state.set_state(ReminderCreateStates.waiting_for_reminder_type)


@router.callback_query(
    StateFilter(ReminderCreateStates.waiting_for_reminder_type),
    F.data == "custom_reminder_type",
)
async def fill_custom_interval(callback: CallbackQuery, state: FSMContext):
    await state.update_data(reminder_type=callback.data)
    await callback.message.edit_text(
        text="Введите свой интервал в формате «1 год 2 месяца 3 дня 4 часа 5 минут»",
        reply_markup=ReminderCreationKeyboards.to_main_menu,
    )
    await state.set_state(ReminderCreateStates.waiting_for_custom_interval)


@router.callback_query(
    StateFilter(ReminderCreateStates.waiting_for_reminder_type),
    F.data != "custom_reminder_type",
)
async def choose_reminder_start_time_from_callback(
    callback: CallbackQuery, state: FSMContext
):
    await state.update_data(reminder_type=callback.data)
    await callback.message.edit_text(
        text="Выберите время начала напоминания",
        reply_markup=ReminderCreationKeyboards.choose_reminder_start_time,
    )
    await state.set_state(ReminderCreateStates.waiting_for_start_time_choice)


@router.message(StateFilter(ReminderCreateStates.waiting_for_custom_interval))
async def choose_reminder_start_time_from_message(message: Message, state: FSMContext):
    await state.update_data(custom_interval=message.text)
    await message.answer(
        text="Выберите время начала напоминания",
        reply_markup=ReminderCreationKeyboards.choose_reminder_start_time,
    )
    await state.set_state(ReminderCreateStates.waiting_for_start_time_choice)


@router.callback_query(
    StateFilter(ReminderCreateStates.waiting_for_start_time_choice),
    F.data == "start_reminder_now",
)
async def confirm_reminder_creation_from_callback(
    callback: CallbackQuery, state: FSMContext
):
    await state.update_data(start_time=callback.data)
    data = await state.get_data()
    await callback.message.edit_text(
        text=f"{data}",
        reply_markup=ReminderCreationKeyboards.confirm_reminder_creation,
    )
    await state.set_state(ReminderCreateStates.waiting_for_reminder_confirmation)


@router.callback_query(
    StateFilter(ReminderCreateStates.waiting_for_start_time_choice),
    F.data == "start_reminder_other_time",
)
async def fill_start_datetime(callback: CallbackQuery, state: FSMContext):
    await state.update_data(start_time_type=callback.data)
    await callback.message.edit_text(
        text="Введите дату начала напоминания в формате «ДД.ММ.ГГГГ ЧЧ:ММ»",
        reply_markup=ReminderCreationKeyboards.to_main_menu,
    )
    await state.set_state(ReminderCreateStates.waiting_for_start_datetime)


@router.message(StateFilter(ReminderCreateStates.waiting_for_start_datetime))
async def confirm_reminder_creation_from_message(message: Message, state: FSMContext):
    await state.update_data(custom_start_time=message.text)
    data = await state.get_data()
    await message.answer(
        text=f"{data}", reply_markup=ReminderCreationKeyboards.confirm_reminder_creation
    )
    await state.set_state(ReminderCreateStates.waiting_for_reminder_confirmation)


@router.callback_query(
    StateFilter(ReminderCreateStates.waiting_for_reminder_confirmation)
)
async def show_creation_confirmation(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        text="Напоминание создано", reply_markup=ReminderCreationKeyboards.to_main_menu
    )
