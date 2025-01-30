from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int

def paginator(total_pages: int, page: int = 0):
    builder = InlineKeyboardBuilder()

    if page > 0:
        builder.add(
            InlineKeyboardButton(text=f"<- Page: {page}", callback_data=Pagination(action="prev", page=page).pack())
        )

    builder.add(InlineKeyboardButton(text=f"Tools {page}", callback_data=f"Tools_{page}"))

    if page < total_pages - 1:
        builder.add(
            InlineKeyboardButton(text=f"Page: {page + 2} ->", callback_data=Pagination(action="next", page=page).pack())
        )

    return builder.as_markup()
