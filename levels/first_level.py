from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder

from models.users import update_user_data, increment_discount
from tools import hide_buttons, carousel_render
from keyboards import to_carousel_keyboard, cancel_game_keyboard

first_level_router: Router = Router()


# First level
@first_level_router.callback_query(F.data == "first_level")
async def first_level_intro(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    next_button = await to_carousel_keyboard(level_num="first")

    level_text = (
        "💡 Уровень 1: Зачем нужен графический дизайн? Бонус за прохождение: скидка <b>+10%</b>."
    )
    cancel_game_button = await cancel_game_keyboard()

    await callback_query.message.answer(
        text=level_text, reply_markup=cancel_game_button.as_markup(resize_keyboard=True)
    )

    next_text = " Перед тем как перейти к первому вопросу, давайте разберемся, почему графический дизайн так важен:"
    await callback_query.message.answer(
        text=next_text,
        reply_markup=next_button.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )


# First level information carousel
@first_level_router.callback_query(F.data.startswith("first_level_carousel"))
async def first_level_carousel(callback_query: CallbackQuery):
    await carousel_render(callback_query=callback_query, level_num="first")


# First level continue
@first_level_router.callback_query(F.data == "first_level_continue")
async def first_level_continue(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    await callback_query.message.answer(
        text="Для получения бонуса, ответь на вопрос:"
    )

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
    await callback_query.message.answer(text=text)

    @first_level_router.message(
        F.text.upper().startswith("МОЙ") | F.text.upper().startswith("МОЯ")
    )
    async def get_answer(message: Message):
        await update_user_data(user_id=message.from_user.id, utp=message.text)
        await increment_discount(user_id=message.from_user.id)

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
