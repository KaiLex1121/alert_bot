from aiogram.filters.state import State, StatesGroup


class CHECK_STATES(StatesGroup):
    TEST_STATE = State()

class MainStates(StatesGroup):
    MAIN_DIALOG = State()
