import random

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

import data
from keyboards import to_carousel_keyboard
from models.users import get_user_data, increment_discount, update_user_data
from tools import add_user_answer, carousel_render, hide_buttons

third_level_router: Router = Router()


# Third level
@third_level_router.callback_query(F.data == "third_level_intro")
async def third_level_intro(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)
    await update_user_data(user_id=callback_query.message.chat.id, lvl_2_ans={})

    next_button = await to_carousel_keyboard(level_num="third")

    text = (
        "🎮 Отлично! Ты прошел второй уровень и теперь готов к бонусному уровню, в котором познакомишься с "
        "нестандартным применением дизайна и технологий для увеличения продаж."
    )
    await callback_query.message.answer(
        text=text,
        reply_markup=next_button.as_markup(resize_keyboard=True),
        parse_mode="HTML",
    )


# Third level information carousel
@third_level_router.callback_query(F.data.startswith("third_level_carousel"))
async def third_level_carousel(callback_query: CallbackQuery):
    await carousel_render(callback_query=callback_query, level_num="third")


# Third level continue
@third_level_router.callback_query(F.data == "third_level_continue")
async def third_level_continue(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    buttons = InlineKeyboardBuilder()
    buttons.add(
        InlineKeyboardButton(text="Получить задание", callback_data="third_level_task"),
        InlineKeyboardButton(
            text="Продолжить без бонусов", callback_data="end_point_intro"
        ),
    )
    buttons.adjust(1)

    text = "А теперь давай закрепим информацию."

    await callback_query.message.answer(
        text=text, reply_markup=buttons.as_markup(resize_keyboard=True)
    )


# Third level task
@third_level_router.callback_query(F.data == "third_level_task")
async def second_level_task_info(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    user = await get_user_data(user_id=callback_query.message.chat.id)
    if user:
        await update_user_data(user_id=user.user_id, lvl_3_ans={})

    task_text = (
        "Задание: выбери верное ли перед тобой утверждение или нет. "
        "Бонус за прохождение уровня: скидка <b>+ 10%</b>"
    )

    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text="Вперед", callback_data="third_solution_"))

    await callback_query.message.answer(
        text=task_text,
        reply_markup=button.as_markup(reply_keyboard=True),
        parse_mode="HTML",
    )


@third_level_router.callback_query(F.data.startswith("third_solution_"))
async def third_level_solution(callback_query: CallbackQuery):
    correct_results = await data.get_third_level_answers()
    user = await get_user_data(user_id=callback_query.message.chat.id)
    user_answers = user.lvl_3_ans

    current_answer = callback_query.data.split("_")[2]
    if current_answer != "":
        user_answers.update({callback_query.message.text: current_answer})
        await update_user_data(user_id=user.user_id, lvl_3_ans=user_answers)

        for key in user_answers.keys():
            correct_results.pop(key)

        await add_user_answer(
            callback_query=callback_query, current_answer=current_answer
        )
    else:
        await hide_buttons(callback_query=callback_query)

    if len(correct_results) != 0:
        answers_keyboard = InlineKeyboardBuilder()
        answers_keyboard.add(
            InlineKeyboardButton(text="Верно", callback_data="third_solution_Верно"),
            InlineKeyboardButton(
                text="Неверно", callback_data="third_solution_Неверно"
            ),
        )
        answers_keyboard.adjust(2)

        answer, text = random.sample(list(correct_results.items()), 1)[0]

        await callback_query.message.answer(
            text=answer, reply_markup=answers_keyboard.as_markup(resize_keyboard=True)
        )
    else:
        await third_level_check_result(callback_query=callback_query)


# Third level result checking
async def third_level_check_result(callback_query: CallbackQuery):
    origin_results = await data.get_third_level_answers()
    user = await get_user_data(user_id=callback_query.message.chat.id)

    if user.lvl_3_ans == origin_results:
        await increment_discount(user_id=callback_query.message.chat.id)

        text = (
            "Поздравляю! Ты успешно преодолел несколько уровней нашей игры и узнал, как графический дизайн может "
            "повысить эффективность твоего бизнеса."
        )

        buttons = InlineKeyboardBuilder()
        buttons.add(
            InlineKeyboardButton(text="К результатам", callback_data="end_point_intro"),
        )

        await update_user_data(user_id=user.user_id, lvl_3_ans={})
        await callback_query.message.answer(
            text=text, reply_markup=buttons.as_markup(resize_keyboard=True)
        )
    else:
        buttons = InlineKeyboardBuilder()
        buttons.add(
            InlineKeyboardButton(
                text="Попробовать снова", callback_data="third_level_task"
            ),
            InlineKeyboardButton(
                text="Продолжить без бонуса", callback_data="end_point_intro"
            ),
        )
        buttons.adjust(1)

        text = (
            "Извини, но ты ответил неверно. Ты можешь попробовать пройти задание снова или продолжить без бонуса. "
            "Выбирай:"
        )

        await callback_query.message.answer(
            text=text, reply_markup=buttons.as_markup(resize_keyboard=True)
        )
