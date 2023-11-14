from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from keyboards import cancel_game_keyboard, to_carousel_keyboard
from models.users import clear_user_data, increment_discount, update_user_data, get_user_data
from tools import carousel_render, hide_buttons

first_level_router: Router = Router()


# First level
@first_level_router.message(F.text.startswith("Старт игры"))
async def first_level_intro(message: Message):
    await clear_user_data(
        user_id=message.from_user.id, username=message.from_user.username
    )

    next_button = await to_carousel_keyboard(level_num="first")

    level_text = "💡 Уровень 1: Зачем нужен графический дизайн? Бонус за прохождение: скидка <b>+10%</b>."
    cancel_game_button = await cancel_game_keyboard()

    await message.answer(
        text=level_text,
        reply_markup=cancel_game_button.as_markup(resize_keyboard=True),
        parse_mode="HTML",
    )

    next_text = " Перед тем как перейти к первому вопросу, давайте разберемся, почему графический дизайн так важен:"
    await message.answer(
        text=next_text,
        reply_markup=next_button.as_markup(resize_keyboard=True),
        parse_mode="HTML",
    )


# First level information carousel
@first_level_router.callback_query(F.data.startswith("first_level_carousel"))
async def first_level_carousel(callback_query: CallbackQuery):
    await carousel_render(callback_query=callback_query, level_num="first")


# First level continue
@first_level_router.callback_query(F.data == "first_level_continue")
async def first_level_continue(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    await callback_query.message.answer(text="Для получения бонуса, ответь на вопрос:")

    first_question_buttons = InlineKeyboardBuilder()
    first_question_buttons.add(
        InlineKeyboardButton(text="Ответить", callback_data="first_level_task"),
        InlineKeyboardButton(text="Продолжить без бонуса", callback_data="skip_to_2"),
    )
    first_question_buttons.adjust(1)

    first_question_text = (
        "🤔Вопрос: А что делает твой продукт или услугу более заметными и привлекательными"
        " для потенциальных клиентов?"
    )

    await callback_query.message.answer(
        text=first_question_text,
        reply_markup=first_question_buttons.as_markup(resize_keyboard=True),
    )


# First level task
@first_level_router.callback_query(F.data == "first_level_task")
async def first_answer_handler(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    text = 'Напиши свой ответ ниже начиная со слов "<b>Мой продукт ...</b>" или "<b>Моя услуга ...</b>"'
    await callback_query.message.answer(text=text, parse_mode="HTML")

    @first_level_router.message(
        F.text.upper().startswith("МОЙ") | F.text.upper().startswith("МОЯ")
    )
    async def get_answer(message: Message):
        user = await get_user_data(user_id=message.from_user.id)
        if user.utp is None:
            await update_user_data(user_id=user.user_id, utp=message.text)
            await increment_discount(user_id=user.user_id)

            next_button = InlineKeyboardBuilder()
            next_button.add(
                InlineKeyboardButton(text="Далее", callback_data="second_level_intro")
            )

            text = (
                "🎮 Отлично! Твои знания о графическом дизайне и его влиянии на бизнес продолжают расти. "
                "Готов к следующему вызову?"
            )

            await message.answer(
                text=text, reply_markup=next_button.as_markup(resize_keyboard=True)
            )
        else:
            ok_button = InlineKeyboardBuilder()
            ok_button.add(
                InlineKeyboardButton(text="Ладно 😔", callback_data="second_level_intro")
            )

            angry_text = (
                "Ты уже отвечал на этот вопрос 😡 Возвращаю тебя на второй уровень 🪄"
            )

            await message.answer(
                text=angry_text,
                reply_markup=ok_button.as_markup(resize_keyboard=True)
            )

