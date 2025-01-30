from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int

def paginator(total_pages: int, page: int = 0):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="Risks", callback_data=Pagination(action="risk", page=page).pack())
    )

    navigation_buttons = []

    if page > 0:
        builder.add(
            InlineKeyboardButton(text=f"<- Page: {page}", callback_data=Pagination(action="prev", page=page).pack())
        )

    builder.add(InlineKeyboardButton(text=f"Page: {page + 1}", callback_data=f"noop"))

    if page < total_pages - 1:
        builder.add(
            InlineKeyboardButton(text=f"Page: {page + 2} ->", callback_data=Pagination(action="next", page=page).pack())
        )

    builder.add(*navigation_buttons)

    builder.adjust(1, 3)

    return builder.as_markup()
