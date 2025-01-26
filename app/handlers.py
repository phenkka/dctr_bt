from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from logs.logging_config import logger
from app.states import Survey
import app.keyboards as kb
import app.utils as utils

router = Router()

last_bot_message_id = None

@router.message(Command("start"))
async def cmd_start(message: Message):
    logger.info(f"The user {message.from_user.id} called the command /start.")
    await message.answer("Here is detailed information about the bot", reply_markup=kb.greeting)

@router.callback_query(F.data == "survey")
async def set_age(query: CallbackQuery, state: FSMContext):
    global last_bot_message_id

    await state.set_state(Survey.age)
    logger.info(f"The user {query.from_user.id}'s state has been set to Survey.age.")

    bot_message = await query.message.edit_text("Let's start. At the beginning, enter your age.")
    last_bot_message_id = bot_message.message_id

@router.message(Survey.age)
async def set_weight(message: Message, state: FSMContext):
    global last_bot_message_id

    await state.update_data(age=message.text)
    await state.set_state(Survey.weight)
    logger.info(f"The user {message.from_user.id}'s state has been set to Survey.weight.")

    await message.delete()
    bot_message = await utils.delete_prev_and_send_new(
        message=message,
        last_bot_message_id=last_bot_message_id,
        new_text="Enter your weight\n<i>(in kilograms)</i>"
    )
    last_bot_message_id = bot_message.message_id

@router.message(Survey.weight)
async def set_height(message: Message, state: FSMContext):
    global last_bot_message_id

    await state.update_data(weight=message.text)
    await state.set_state(Survey.height)
    logger.info(f"The user {message.from_user.id}'s state has been set to Survey.height.")

    await message.delete()
    bot_message = await utils.delete_prev_and_send_new(
        message=message,
        last_bot_message_id=last_bot_message_id,
        new_text="Enter your height\n<i>(in centimeters)</i>"
    )
    last_bot_message_id = bot_message.message_id

@router.message(Survey.height)
async def set_feet(message: Message, state: FSMContext):
    global last_bot_message_id

    await state.update_data(height=message.text)
    await state.set_state(Survey.feet)
    logger.info(f"The user {message.from_user.id}'s state has been set to Survey.feet.")

    await message.delete()
    bot_message = await utils.delete_prev_and_send_new(
        message=message,
        last_bot_message_id=last_bot_message_id,
        new_text="Enter your feet\n<i>(EU size)</i>"
    )
    last_bot_message_id = bot_message.message_id

@router.message(Survey.feet)
async def set_gender(message: Message, state: FSMContext):
    global last_bot_message_id

    await state.update_data(feet=message.text)
    await state.set_state(Survey.gender)
    logger.info(f"The user {message.from_user.id}'s state has been set to Survey.gender.")

    await message.delete()
    await utils.delete_prev_and_send_new(
        message=message,
        last_bot_message_id=last_bot_message_id,
        new_text="What's your gender?"
    )

@router.callback_query(Survey.gender)
async def set_gender(query: CallbackQuery, state: FSMContext):
    genders = query.data
    await state.update_data(gender=genders)

    if genders == "female":
        await state.set_state(Survey.pregnant)
        logger.info(f"The user {query.from_user.id}'s state has been set to Survey.pregnant.")
        await query.message.edit_text("Are you pregnant?", reply_markup=kb.yon)
    else:
        await state.update_data(pregnant="no")
        await state.set_state(Survey.smoking)
        logger.info(f"The user {query.from_user.id}'s state has been set to Survey.smoking.")
        await query.message.edit_text("Are you smoking?", reply_markup=kb.yon)

@router.callback_query(Survey.pregnant)
async def set_pregnant(query: CallbackQuery, state: FSMContext):
    await state.update_data(pregnant=query.data)
    await state.set_state(Survey.smoking)
    logger.info(f"The user {query.from_user.id}'s state has been set to Survey.smoking.")
    await query.message.edit_text("Are you smoking?", reply_markup=kb.yon)

@router.callback_query(Survey.smoking)
async def set_smoking(query: CallbackQuery, state: FSMContext):
    await state.update_data(smoking=query.data)
    await state.set_state(Survey.sex)
    logger.info(f"The user {query.from_user.id}'s state has been set to Survey.sex.")
    await query.message.edit_text("Are you sexually active?", reply_markup=kb.yon)

@router.callback_query(Survey.sex)
async def set_sex(query: CallbackQuery, state: FSMContext):
    await state.update_data(sexually_active=query.data)
    await state.clear()
    logger.info(f"The user {query.from_user.id}'s state has been clean.")
    await query.message.edit_text("Thank you for completing the survey!")