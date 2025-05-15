from aiogram.fsm.state import State, StatesGroup


class Work(StatesGroup):
    process = State()
class Work(StatesGroup):
    process = State()
    waiting_for_photo = State()
    waiting_for_meme_text = State()