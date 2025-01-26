from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

greeting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Take the survey", callback_data="survey")]
])

gender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Male", callback_data="male"),
     InlineKeyboardButton(text='Female', callback_data="female")]
])

yon = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Yes", callback_data="yes"),
     InlineKeyboardButton(text="No", callback_data="no")]
])