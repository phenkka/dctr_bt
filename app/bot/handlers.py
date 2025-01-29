from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import os
from contextlib import suppress

from logs.logging_config import logger
from bot.states import Survey
from bot.scripts.algoritm import Database
import bot.keyboards as kb
import bot.pagination as pg

db = Database(min_conn=1, max_conn=25,
               dbname=os.getenv("POSTGRES_DB"),
               user=os.getenv("POSTGRES_USER"),
               password=os.getenv("POSTGRES_PASSWORD"),
               host=os.getenv("POSTGRES_HOST"),
               port=os.getenv("POSTGRES_PORT"))
router = Router()



@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """The command /start"""
    await state.clear()

    logger.info(f"The user {message.from_user.id} called the command /start.")
    await message.answer("Here is detailed information about the bot", reply_markup=kb.greeting)

@router.callback_query(F.data == "survey")
async def set_age(query: CallbackQuery, state: FSMContext):
    """The first question about age"""
    await state.set_state(Survey.age)
    logger.info(f"The user {query.from_user.id}'s state has been set to Survey.age.")

    await query.message.edit_text("Let's start. At the beginning, enter your age.")

@router.message(Survey.age)
async def set_weight(message: Message, state: FSMContext):
    """The second question about weight"""
    user_id = message.from_user.id
    user_message = message.text

    if 0 < int(user_message) < 120:
        await state.update_data(age=user_message)
        await state.set_state(Survey.weight)
        logger.info(f"The user {user_id}'s state has been set to Survey.weight.")

        await message.answer("Enter your weight\n<i>(in kilograms)</i>.", parse_mode='HTML')
    else:
        await message.answer("Please enter a valid age.")

@router.message(Survey.weight)
async def set_height(message: Message, state: FSMContext):
    """The third question about height"""
    user_message = message.text
    user_id = message.from_user.id

    if 1 < int(user_message) < 700:
        await state.update_data(weight=user_message)
        await state.set_state(Survey.height)
        logger.info(f"The user {user_id}'s state has been set to Survey.height.")

        await message.answer("Enter your height\n<i>(in centimeters)</i>.", parse_mode='HTML')
    else:
        await message.answer("Please enter a valid weight in kilograms.")

@router.message(Survey.height)
async def set_feet(message: Message, state: FSMContext):
    """The fourth question about feet"""
    user_message = message.text

    if 25 < int(user_message) < 300:
        await state.update_data(height=message.text)
        await state.set_state(Survey.feet)
        logger.info(f"The user {message.from_user.id}'s state has been set to Survey.feet.")

        await message.answer("Enter your feet\n<i>(EU size)</i>.", parse_mode='HTML')
    else:
        await message.answer("Please enter a valid height in centimeters.")

@router.message(Survey.feet)
async def set_gender(message: Message, state: FSMContext):
    """The fifth question about gender"""
    user_message = message.text
    user_id = message.from_user.id

    if 15 < int(user_message) < 80:
        await state.update_data(feet=user_message)
        await state.set_state(Survey.gender)
        logger.info(f"The user {user_id}'s state has been set to Survey.gender.")

        await message.answer("What's your gender?", reply_markup=kb.gender)
    else:
        await message.answer("Please enter a valid feet size.")

@router.callback_query(Survey.gender)
async def set_gender(query: CallbackQuery, state: FSMContext):
    """Specific question about pregnant if gender is female"""
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
    """The sixth question about smoking"""
    await state.update_data(pregnant=query.data)
    await state.set_state(Survey.smoking)
    logger.info(f"The user {query.from_user.id}'s state has been set to Survey.smoking.")

    await query.message.edit_text("Are you smoking?", reply_markup=kb.yon)

@router.callback_query(Survey.smoking)
async def set_smoking(query: CallbackQuery, state: FSMContext):
    """The last question about sex activity"""
    await state.update_data(smoking=query.data)
    await state.set_state(Survey.sex)
    logger.info(f"The user {query.from_user.id}'s state has been set to Survey.sex.")

    await query.message.edit_text("Are you sexually active?", reply_markup=kb.yon)


@router.callback_query(pg.Pagination.filter(F.action.in_(["prev", "next"])))
async def pagination_query(query: CallbackQuery, callback_data: pg.Pagination, state: FSMContext):
    data = await state.get_data()
    recommendations = data.get("recommendations", [])

    await state.clear()
    logger.info(f"The user {query.from_user.id}'s state has been clean.")

    page_num = int(callback_data.page)
    page = page_num - 1 if page_num > 0 else 0

    if callback_data.action == "next":
        page = page_num + 1 if page_num < (len(fake_data) - 1) else page_num

    with suppress(TelegramBadRequest):
        await query.message.edit_text(f"{recommendations[page][0]}"
                               f"\n<b>{recommendations[page][1]}</b>"
                               f"\n{recommendations[page][2]}"
                               f"\n{recommendations[page][3]}"
                               f"\n{recommendations[page][4]}", reply_markup=pg.paginator(page=page, total_pages=4), parse_mode='HTML'
        )
    await query.answer()


@router.callback_query(Survey.sex)
async def set_sex(query: CallbackQuery, state: FSMContext):
    """The survey result"""
    await state.update_data(sex=query.data)
    data = await state.get_data()

    recommendations = db.get_recommendation(data)
    await state.update_data(recommendations=recommendations)

    await query.message.edit_text("Thank you for completing the survey! Your answers:")
    await query.message.answer(f"{recommendations[0][0]}"
                               f"\n<b>{recommendations[0][1]}</b>"
                               f"\n{recommendations[0][2]}"
                               f"\n{recommendations[0][3]}"
                               f"\n{recommendations[0][4]}", reply_markup=pg.paginator(total_pages=4), parse_mode='HTML')