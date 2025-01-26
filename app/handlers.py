from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from logs.logging_config import logger

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    logger.info(f"The user {message.from_user.id} called the command /start")
    await message.answer("Здесь подробная информация о боте")