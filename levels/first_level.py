from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder

import data
from models.users import update_user_data, increment_discount
from tools import hide_buttons, carousel_render
from keyboards import to_carousel_keyboard, cancel_game_keyboard

first_level_router: Router = Router()


# First level
@first_level_router.callback_query(F.data == "first_level")
async def first_level_intro(callback_query: CallbackQuery):
    # Hide inline button from previous message
    await hide_buttons(callback_query=callback_query)

    next_button = await to_carousel_keyboard(level="first_level")

    level_text = "💡 Уровень 1: Зачем нужен графический дизайн? Бонус за прохождение: скидка 10%"
    cancel_game_button = await cancel_game_keyboard()

    await callback_query.message.answer(
        text=level_text,
        reply_markup=cancel_game_button.as_markup(resize_keyboard=True)
    )

    next_text = " Перед тем как перейти к первому вопросу, давайте разберемся, почему графический дизайн так важен:"
    await callback_query.message.answer(
        text=next_text,
        reply_markup=next_button.as_markup(resize_keyboard=True),
    )


# First level information carousel
@first_level_router.callback_query(F.data.startswith("first_level_carousel"))
async def first_level_carousel(callback_query: CallbackQuery):
    level = callback_query.data[:callback_query.data.find("level") + 5]

    await carousel_render(callback_query=callback_query, level=level)


# First level continue
@first_level_router.callback_query(F.data == "first_level_continue")
async def first_level_continue(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    await callback_query.message.answer(text="Для получения бонуса, ответьте на вопрос:")

    first_question_buttons = InlineKeyboardBuilder()
    first_question_buttons.add(
        InlineKeyboardButton(text="Ответить", callback_data="first_level_task")
    )
    first_question_buttons.add(
        InlineKeyboardButton(
            text="Продолжить без бонуса", callback_data="skip_to_2"
        )
    )

    first_question_text = (
        "🤔Вопрос: А что делает ваш продукт или услугу более заметными и привлекательными"
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

    text = ("Напишите свой ответ ниже начиная со слов 'Мой продукт ...' или 'Моя услуга ...'")
    await callback_query.message.answer(text=text)


@first_level_router.message(F.text.upper().in_(data.FIRST_LEVEL_ANSWER_TRIGGER))
async def get_answer(message: Message):

    await update_user_data(user_id=message.from_user.id, utp=message.text)
    await increment_discount(user_id=message.from_user.id)

    next_button = InlineKeyboardBuilder()
    next_button.add(
        InlineKeyboardButton(text="Далее", callback_data="second_level_intro")
    )

    text = (
        "🎮 Отлично! Ваши знания о графическом дизайне и его влиянии на бизнес продолжают расти. "
        "Готовы к следующему вызову?"
    )

    await message.answer(
        text=text, reply_markup=next_button.as_markup(resize_keyboard=True)
    )
