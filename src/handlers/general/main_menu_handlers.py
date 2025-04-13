from aiogram import Bot, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.redis import Redis
from aiogram.types import CallbackQuery, Message
from src.states.general_states import MainStates
from src.services.main_menu_render import render_main_menu
from src.database.dao.holder import HolderDAO
from src.states.general_states import CHECK_STATES

router: Router = Router()

@router.message(Command("start"))
async def get_started(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(MainStates.MAIN_DIALOG)
    await render_main_menu(
        message=message,
        state=state,
        bot=bot,
        message_to_delete=1
    )
