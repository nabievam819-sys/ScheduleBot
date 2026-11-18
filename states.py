from aiogram.fsm.state import State, StatesGroup


class AddLessonStates(StatesGroup):
    day = State()
    subject = State()
    time = State()
    room = State()
