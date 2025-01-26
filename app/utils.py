from aiogram.types import Message

from logs.logging_config import logger
import app.keyboards as kb

async def delete_prev_and_send_new(message: Message, last_bot_message_id: int, new_text: str):
    try:
        if last_bot_message_id:
            await message.chat.delete_message(last_bot_message_id)
    except Exception as e:
        logger.error(f"Error deleting message: {e}")

    if new_text == "What's your gender?":
        bot_message = await message.answer(new_text, reply_markup=kb.gender, parse_mode='HTML')
    else:
        bot_message = await message.answer(new_text, parse_mode='HTML')
    return bot_message