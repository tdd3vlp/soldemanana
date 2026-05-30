from aiogram.fsm.state import State, StatesGroup


class ConversationStates(StatesGroup):
    active = State()
