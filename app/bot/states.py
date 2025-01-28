from aiogram.fsm.state import StatesGroup, State

class Survey(StatesGroup):
    age = State()
    weight = State()
    height = State()
    feet = State()
    gender = State()
    pregnant = State()
    smoking = State()
    sex = State()
    recommendations = State()