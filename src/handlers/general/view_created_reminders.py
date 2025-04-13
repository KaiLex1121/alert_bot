from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import Redis
from aiogram.types import CallbackQuery, Message

from src.database.dao.holder import HolderDAO
from src.keyboards.view_created_reminders import ViewCreatedRemindersKeyboards
router: Router = Router()

@router.callback_query(F.data == "show_created_reminders")
async def show_created_reminders(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выберите нужное действие",
        reply_markup=ViewCreatedRemindersKeyboards.show_created_reminders
    )
