import random
from time import sleep

import aiogram.exceptions
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

import data
from keyboards import to_carousel_keyboard
from models.users import get_user_data, increment_discount, update_user_data
from tools import add_user_answer, carousel_render, hide_buttons

second_level_router: Router = Router()


# Second level
@second_level_router.callback_query(F.data == "second_level_intro")
async def second_level_intro(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    introdution_text = (
        "🌟 Уровень 2: Как можно увеличить продажи с помощью дизайна? "
        "Бонус за прохождение уровня: скидка <b>+10%</b> или <b>+20%</b>."
    )

    await callback_query.message.answer(text=introdution_text, parse_mode="HTML")
    sleep(1)

    next_button = await to_carousel_keyboard(level_num="second")

    await callback_query.message.answer(
        text="Теперь давай перейдем к методам увеличения продаж с помощью графики:",
        reply_markup=next_button.as_markup(resize_keyboard=True),
    )


# Second level information carousel
@second_level_router.callback_query(F.data.startswith("second_level_carousel"))
async def second_level_carousel(callback_query: CallbackQuery):
    await carousel_render(callback_query=callback_query, level_num="second")


# Second level continue
@second_level_router.callback_query(F.data == "second_level_continue")
async def second_level_continue(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    buttons = InlineKeyboardBuilder()
    buttons.add(
        InlineKeyboardButton(
            text="Получить задание", callback_data="second_level_task"
        ),
        InlineKeyboardButton(text="Продолжить без бонусов", callback_data="bonus_task"),
    )
    buttons.adjust(1)

    text = "Перед тем как идти дальше, давай закрепим информацию на примерах."
    await callback_query.message.answer(
        text=text, reply_markup=buttons.as_markup(resize_keyboard=True)
    )


# Second level task
@second_level_router.callback_query(F.data == "second_level_task")
async def second_level_task_info(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    user = await get_user_data(user_id=callback_query.message.chat.id)
    if user:
        await update_user_data(user_id=user.user_id, lvl_2_ans={})

    task_text = "Задание: Сопоставь бренд и его описание."

    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text="Вперед", callback_data="second_solution_"))

    await callback_query.message.answer(
        text=task_text, reply_markup=button.as_markup(reply_keyboard=True)
    )


@second_level_router.callback_query(F.data.startswith("second_solution_"))
async def second_level_solution(callback_query: CallbackQuery):
    correct_results = await data.get_second_level_answers()
    user = await get_user_data(user_id=callback_query.message.chat.id)
    user_answers = user.lvl_2_ans

    current_answer = callback_query.data.split("_")[2]
    if current_answer != "":
        user_answers.update({current_answer: callback_query.message.text})
        await update_user_data(user_id=user.user_id, lvl_2_ans=user_answers)

        for key in user_answers.keys():
            correct_results.pop(key)

        await add_user_answer(
            callback_query=callback_query, current_answer=current_answer
        )
    else:
        await hide_buttons(callback_query=callback_query)

    if len(correct_results) != 0:
        answers_keyboard = InlineKeyboardBuilder()
        for key in correct_results.keys():
            answers_keyboard.add(
                InlineKeyboardButton(text=key, callback_data=f"second_solution_{key}")
            )
        answers_keyboard.adjust(2)

        answer, text = random.sample(list(correct_results.items()), 1)[0]

        await callback_query.message.answer(
            text=text, reply_markup=answers_keyboard.as_markup(resize_keyboard=True)
        )
    else:
        await second_level_check_result(callback_query=callback_query)


# Second level result checking
async def second_level_check_result(callback_query: CallbackQuery):
    origin_results = await data.get_second_level_answers()
    user = await get_user_data(user_id=callback_query.message.chat.id)

    if user.lvl_2_ans == origin_results:
        await increment_discount(user_id=callback_query.message.chat.id)

        text = (
            "Поздравляю! Ты ответил правильно, держи <b>10%</b> скидки 🥳. Ты можешь получить еще <b>10%</b>, если "
            "ответишь на бонусный вопрос."
        )

        buttons = InlineKeyboardBuilder()
        buttons.add(
            InlineKeyboardButton(text="Получить бонус", callback_data="bonus_task"),
            InlineKeyboardButton(
                text="Продолжить без бонуса", callback_data="skip_to_3"
            ),
        )
        buttons.adjust(1)

        await callback_query.message.answer(
            text=text,
            reply_markup=buttons.as_markup(resize_keyboard=True),
            parse_mode="HTML",
        )
    else:
        buttons = InlineKeyboardBuilder()
        buttons.add(
            InlineKeyboardButton(
                text="Попробовать снова", callback_data="second_level_task"
            ),
            InlineKeyboardButton(text="Получить бонус", callback_data="bonus_task"),
            InlineKeyboardButton(
                text="Продолжить без бонуса", callback_data="skip_to_3"
            ),
        )
        buttons.adjust(1)

        text = (
            "Извини, но ты ответил неверно. Ты можешь попробовать пройти задание снова, либо получить "
            "<b>10%</b> скидку ответив на бонусный вопрос или продолжить без бонусов. Выбирай:"
        )

        await callback_query.message.answer(
            text=text,
            reply_markup=buttons.as_markup(resize_keyboard=True),
            parse_mode="HTML",
        )


# Second level bonus task
@second_level_router.callback_query(F.data == "bonus_task")
async def bonus_task(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    text = (
        "Бонусное задание - напиши, какие плюсы и минусы ты заметили у своей компании?"
        ' \nНапиши свой ответ ниже начиная со слов <b>"Плюсы ...</b>" или "<b>Минусы ...</b>".'
    )

    user = await get_user_data(user_id=callback_query.message.chat.id)

    if user.lvl_2_ans == {}:
        text = text + '\n\nИли можешь нажать кнопку "<b>Продолжить без бонусов</b>".'

        buttons = InlineKeyboardBuilder()
        buttons.add(
            InlineKeyboardButton(
                text="Продолжить без бонусов", callback_data="skip_to_3"
            ),
        )
        buttons.adjust(1)
        bonus_message = await callback_query.message.answer(
            text=text,
            reply_markup=buttons.as_markup(resize_keyboard=True),
            parse_mode="HTML",
        )
    else:
        await callback_query.message.answer(text=text, parse_mode="HTML")

    @second_level_router.message(
        F.text.upper().startswith("ПЛЮС") | F.text.upper().startswith("МИНУС")
    )
    async def get_answer(message: Message):
        try:
            await hide_buttons(message=bonus_message)
        except aiogram.exceptions.TelegramBadRequest:
            pass
        user_id = message.from_user.id
        await increment_discount(user_id=user_id)
        await update_user_data(user_id=user_id, pain=message.text, lvl_2_ans={})

        next_button = InlineKeyboardBuilder()
        next_button.add(
            InlineKeyboardButton(text="Далее", callback_data="third_level_intro")
        )

        text = (
            "Твой ответ принят. Держи еще <b>10%</b> скидки на мои услуги 😊 "
            "Готов к следующему вызову?"
        )

        await message.answer(
            text=text,
            reply_markup=next_button.as_markup(resize_keyboard=True),
            parse_mode="HTML",
        )
