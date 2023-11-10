import random

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder

from bot import bot
import data
from models.users import User, get_user_data, update_user_data, clear_user_data, increment_discount
from tools import hide_buttons, carousel_render
from keyboards import to_carousel_keyboard

second_level_router: Router = Router()


# Second level
@second_level_router.callback_query(F.data == "second_level_intro")
async def second_level_intro(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    introdution_text = (
        "🌟 Уровень 2: Как можно увеличить продажи с помощью дизайна?"
        "Бонус за прохождение уровня: скидка +10% или +20%"
    )

    await callback_query.message.answer(text=introdution_text)

    next_button = await to_carousel_keyboard(level="second_level")

    await callback_query.message.answer(
        text="Теперь давайте перейдем к методам увеличения продаж с помощью графики:",
        reply_markup=next_button.as_markup(resize_keyboard=True),
    )


# Second level information carousel
@second_level_router.callback_query(F.data.startswith("second_level_carousel"))
async def second_level_carousel(callback_query: CallbackQuery):
    level = callback_query.data[:callback_query.data.find("level") + 5]

    await carousel_render(callback_query=callback_query, level=level)


# Second level continue
@second_level_router.callback_query(F.data == "second_level_continue")
async def second_level_continue(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    buttons = InlineKeyboardBuilder()
    buttons.add(
        InlineKeyboardButton(text="Получить задание", callback_data="second_level_task"),
        InlineKeyboardButton(text="Продолжить без бонусов", callback_data="skip_to_3")
    )

    text = "Перед тем как идти дальше, давайте закрепим информацию на примерах."
    await callback_query.message.answer(
        text=text,
        reply_markup=buttons.as_markup(resize_keyboard=True)
    )


# Second level task
@second_level_router.callback_query(F.data == "second_level_task")
async def second_level_task_info(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    task_text = "Задание: Сопоставьте бренд и его описание"

    origin_results = await data.get_second_level_answers()
    user_results = {}
    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text="Вперед", callback_data="answer_"))

    await callback_query.message.answer(
        text=task_text,
        reply_markup=button.as_markup(reply_keyboard=True)
    )

    @second_level_router.callback_query(F.data.startswith("answer_"))
    async def second_level_answers(callback_query_a: CallbackQuery):

        current_answer: str = ""

        try:
            current_answer = callback_query_a.data.split("_")[1]
            origin_results.pop(current_answer)
        except (KeyError, IndexError):
            pass

        if current_answer != "":
            user_results.update({current_answer: callback_query_a.message.text})

            await bot.edit_message_text(
                chat_id=callback_query_a.message.chat.id,
                message_id=callback_query_a.message.message_id,
                text=callback_query_a.message.text + f"\nВаш ответ: {current_answer}"
            )
        else:
            await hide_buttons(callback_query=callback_query_a)

        if len(origin_results) == 0:
            await hide_buttons(callback_query=callback_query_a)
            await second_level_check_result(
                callback_query=callback_query_a,
                user_results=user_results
            )

        answers_keyboard = InlineKeyboardBuilder()
        for key in origin_results.keys():
            answers_keyboard.add(InlineKeyboardButton(text=key, callback_data=f"answer_{key}"))
        answers_keyboard.adjust(2)

        answer, text = random.sample(list(origin_results.items()), 1)[0]

        await callback_query_a.message.answer(
            text=text,
            reply_markup=answers_keyboard.as_markup(resize_keyboard=True)
        )


# Second level result checking
async def second_level_check_result(callback_query: CallbackQuery, user_results: dict):
    origin_results = await data.get_second_level_answers()
    if user_results == origin_results:
        await increment_discount(user_id=callback_query.message.chat.id)

        text = ("Поздравляю! Ты ответил правильно, держи 10% скидки 🥳. Ты можешь получить еще 10% если ответишь на "
                "бонусный вопрос")

        buttons = InlineKeyboardBuilder()
        buttons.add(
            InlineKeyboardButton(text="Получить бонус", callback_data="bonus_task"),
            InlineKeyboardButton(text="Продолжить без бонуса", callback_data="skip_to_3"),
        )

        await callback_query.message.answer(
            text=text,
            reply_markup=buttons.as_markup(resize_keyboard=True)
        )
    else:
        buttons = InlineKeyboardBuilder()
        buttons.add(
            InlineKeyboardButton(text="Попробовать снова", callback_data="second_level_task"),
            InlineKeyboardButton(text="Получить бонус", callback_data="bonus_task"),
            InlineKeyboardButton(text="Продолжить без бонуса", callback_data="skip_to_3"),
        )
        buttons.adjust(1)

        text = ("Извини, но ты ответил неверно. Ты можешь попробовать пройти задание снова, либо получить "
                "10% скидку ответив на бонусный вопрос или продолжить без бонусов. Выбирай:")

        await callback_query.message.answer(
            text=text,
            reply_markup=buttons.as_markup(resize_keyboard=True)
        )


# Second level bonus task
@second_level_router.callback_query(F.data == "bonus_task")
async def bonus_task(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    text = ("Бонусное задание - напишите, какие плюсы и минусы вы заметили у своей компании?"
            "Напишите свой ответ ниже начиная со слов 'Плюсы ...', 'Минусы ...', 'К ...', 'Из...'")
    await callback_query.message.answer(text=text)


@second_level_router.message(F.text.upper().contains(data.SECOND_LEVEL_ANSWER_TRIGGER))
async def get_answer(message: Message):

    user_id = message.from_user.id
    await increment_discount(user_id=user_id)
    await update_user_data(user_id=user_id, pain=message.text)

    next_button = InlineKeyboardBuilder()
    next_button.add(
        InlineKeyboardButton(text="Далее", callback_data="third_level_intro")
    )

    text = (
        "🎮 Отлично! Ваши знания о графическом дизайне и его влиянии на бизнес продолжают расти. "
        "Готовы к следующему вызову?"
    )

    await message.answer(
        text=text,
        reply_markup=next_button.as_markup(resize_keyboard=True)
    )
