from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

greeting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Take the survey", callback_data="survey")]
])