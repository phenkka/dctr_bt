from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from contextlib import suppress
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from logs.logging_config import logger
from bot.states import Survey
import bot.keyboards as kb
import bot.pagination as pg

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, db):
    """The command /start"""
    await state.clear()  # Очищаем прошлые данные

    # Сохраняем db в состоянии FSM
    await state.update_data(db=db)

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

    if user_message.isdigit() and 0 < int(user_message) < 120:
        await state.update_data(age=int(user_message))
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

    if user_message.isdigit() and 1 < int(user_message) < 700:
        await state.update_data(weight=int(user_message))
        await state.set_state(Survey.height)
        logger.info(f"The user {user_id}'s state has been set to Survey.height.")

        await message.answer("Enter your height\n<i>(in centimeters)</i>.", parse_mode='HTML')
    else:
        await message.answer("Please enter a valid weight in kilograms.")


@router.message(Survey.height)
async def set_feet(message: Message, state: FSMContext):
    """The fourth question about feet"""
    user_message = message.text

    if user_message.isdigit() and 25 < int(user_message) < 300:
        await state.update_data(height=int(user_message))
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

    if user_message.isdigit() and 20 < int(user_message) < 50:  # ✅ Исправлен диапазон
        await state.update_data(feet=int(user_message))
        await state.set_state(Survey.gender)
        logger.info(f"The user {user_id}'s state has been set to Survey.gender.")

        await message.answer("What's your gender?", reply_markup=kb.gender)
    else:
        await message.answer("Please enter a valid feet size.")


@router.callback_query(Survey.gender)
async def set_gender(query: CallbackQuery, state: FSMContext):
    """Specific question about pregnant if gender is female"""
    gender = query.data
    await state.update_data(gender=gender)

    if gender == "female":
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

    if not recommendations or not isinstance(recommendations, list):
        await query.answer("No recommendations found.")
        return

    page_num = int(callback_data.page)
    total_pages = len(recommendations)

    if callback_data.action == "next":
        page = min(page_num + 1, total_pages - 1)
    else:
        page = max(page_num - 1, 0)

    rec = recommendations[page]

    with suppress(TelegramBadRequest):
        await query.message.edit_text(
            f"{rec.get('title', 'No title')} "
            f"<b>{rec.get('grade', 'No grade')}</b> "
            f"{rec.get('text', 'No description')} "
            f"{rec.get('servfreq', '')} "
            f"{rec.get('risktext', '')}",
            reply_markup=pg.paginator(page=page, total_pages=total_pages),
            parse_mode='HTML'
        )
    
    await query.answer()

@router.callback_query(Survey.sex)
async def set_sex(query: CallbackQuery, state: FSMContext):
    await state.update_data(sex=query.data)
    data_from_state = await state.get_data()
    logger.info(f"State data: {data_from_state}")
    
    db = data_from_state.get("db")

    try:
        recommendations = await db.get_recommendation(data_from_state)

        if not recommendations or not isinstance(recommendations, list):
            logger.error(f"Invalid recommendations format: {recommendations}")
            await query.message.answer("No recommendations found.")
            return

        await state.update_data(recommendations=recommendations)

        await query.message.edit_text("Thank you for completing the survey! Your answers:")
        await query.message.answer(
            f"{recommendations[0].get('title', 'No title')}\n"
            f"<b>{recommendations[0].get('grade', 'No grade')}</b>\n"
            f"{recommendations[0].get('text', 'No description')}\n"
            f"{recommendations[0].get('servfreq', '')}\n"
            f"{recommendations[0].get('risktext', '')}",
            reply_markup=pg.paginator(total_pages=len(recommendations)),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        await query.message.answer("An error occurred while processing your request. Please try again later.")


@router.callback_query(F.data.startswith("Tools_"))
async def show_tools(query: CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопку Tools"""
    try:
        page = int(query.data.split("_")[1])
        await state.update_data(current_page=page)
        logger.info(f"Выбрана страница Tools: {page}")

        await query.message.edit_text(
            "Вот инструменты, которые вы запросили. Выберите действие:", 
            reply_markup=InlineKeyboardBuilder()
                .add(InlineKeyboardButton("Назад", callback_data="back"))
                .as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке кнопки Tools: {e}")
        await query.message.answer("Произошла ошибка при обработке запроса.")


@router.callback_query(F.data == "back")
async def go_back(query: CallbackQuery, state: FSMContext):
    """Handle the Back button click to return to the recommendations list"""
    data_from_state = await state.get_data()
    page = data_from_state.get('current_page', 0)

    # Return back to the recommendations list with pagination
    recommendations = data_from_state.get("recommendations", [])
    total_pages = len(recommendations)
    
    await query.message.edit_text(
        f"Thank you for completing the survey! Your answers:\n"
        f"{recommendations[page].get('title', 'No title')}\n"
        f"<b>{recommendations[page].get('grade', 'No grade')}</b>\n"
        f"{recommendations[page].get('text', 'No description')}\n"
        f"{recommendations[page].get('servfreq', '')}\n"
        f"{recommendations[page].get('risktext', '')}",
        reply_markup=pg.paginator(total_pages=total_pages, page=page),
        parse_mode='HTML'
    )
