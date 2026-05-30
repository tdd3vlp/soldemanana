from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    waiting_level = State()
    waiting_goal = State()
    waiting_correction_intensity = State()


class ConversationStates(StatesGroup):
    active = State()


class SettingsStates(StatesGroup):
    main = State()
    waiting_level = State()
    waiting_goal = State()
    waiting_correction = State()
