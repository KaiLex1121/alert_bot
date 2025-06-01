import datetime
import logging
from zoneinfo import ZoneInfo

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import Redis
from aiogram.types import CallbackQuery, Message

from src.database.dao.holder import HolderDAO
from src.keyboards.reminder_management import ReminderManagementKeyboards
from src.services.reminder import ReminderService
from src.services.scheduler import SchedulerService
from src.text.formatters.reminder_management import get_formatted_reminder_text

logger = logging.getLogger(__name__)
router: Router = Router()


@router.callback_query(F.data.startswith("disable_reminder"))
async def disable_reminder(
    callback: CallbackQuery,
    reminder_service: ReminderService,
    dao: HolderDAO,
    scheduler_service: SchedulerService,
):
    reminder_id = int(callback.data.split(":")[1])
    updated_reminder_status = await reminder_service.disable_reminder(
        dao=dao, reminder_id=reminder_id, scheduler_service=scheduler_service
    )
    await callback.message.edit_text(
        text="Напоминание отключено",
        reply_markup=ReminderManagementKeyboards.get_reminder_management_keyboard_by_status(
            reminder_id, updated_reminder_status
        ),
    )


@router.callback_query(F.data.startswith("enable_reminder"))
async def enable_reminder(
    callback: CallbackQuery,
    reminder_service: ReminderService,
    dao: HolderDAO,
    scheduler_service: SchedulerService,
):
    reminder_id = int(callback.data.split(":")[1])
    updated_reminder_status = await reminder_service.enable_reminder(
        dao=dao, reminder_id=reminder_id, scheduler_service=scheduler_service
    )
    await callback.message.edit_text(
        text="Напоминание включено",
        reply_markup=ReminderManagementKeyboards.get_reminder_management_keyboard_by_status(
            reminder_id, updated_reminder_status
        ),
    )


@router.callback_query(F.data.startswith("enable_reminder"))
async def enable_reminder_with_reset(
    callback: CallbackQuery,
    reminder_service: ReminderService,
    dao: HolderDAO,
    scheduler_service: SchedulerService,
):
    reminder_id = int(callback.data.split(":")[1])
    updated_reminder_status = await reminder_service.enable_reminder(
        dao=dao, reminder_id=reminder_id, scheduler_service=scheduler_service
    )
    await callback.message.edit_text(
        text="Напоминание включено",
        reply_markup=ReminderManagementKeyboards.get_reminder_management_keyboard_by_status(
            reminder_id, updated_reminder_status
        ),
    )


@router.callback_query(F.data.startswith("delete_reminder"))
async def delete_reminder(
    callback: CallbackQuery,
    reminder_service: ReminderService,
    dao: HolderDAO,
    scheduler_service: SchedulerService,
):
    reminder_id = int(callback.data.split(":")[1])
    await reminder_service.delete_reminder(
        dao=dao, reminder_id=reminder_id, scheduler_service=scheduler_service
    )
    await callback.message.edit_text(text="Напоминание удалено")


@router.callback_query(F.data.startswith("reset_reminder_start_time"))
async def reset_reminder_start_time(
    callback: CallbackQuery,
    reminder_service: ReminderService,
    dao: HolderDAO,
    scheduler_service: SchedulerService,
):
    reminder_id = int(callback.data.split(":")[1])
    reminder = await reminder_service.reset_reminder_start_time(
        dao=dao, reminder_id=reminder_id, scheduler_service=scheduler_service
    )
    formatted_reminder_text = get_formatted_reminder_text(reminder)
    if reminder.start_datetime < datetime.datetime.now(ZoneInfo("Europe/Moscow")):
        await callback.answer(text="Время начала напоминания сброшено")
        await callback.message.edit_text(
            text=formatted_reminder_text,
            reply_markup=ReminderManagementKeyboards.get_reminder_management_keyboard_by_status(
                reminder_id, reminder.is_active
            ),
        )
    else:
        await callback.answer(
            "У этого типа напоминаний нельзя сбросить время начала напоминания"
        )
        await callback.message.edit_text(
            text=formatted_reminder_text,
            reply_markup=ReminderManagementKeyboards.get_reminder_management_keyboard_by_status(
                reminder_id, reminder.is_active
            ),
        )
