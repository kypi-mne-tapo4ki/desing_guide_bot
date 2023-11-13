from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder

import data
from keyboards import to_carousel_keyboard
from tools import hide_buttons, carousel_render


third_level_router: Router = Router()


# Third level
@third_level_router.callback_query(F.data == "third_level_intro")
async def third_level_intro(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    next_button = await to_carousel_keyboard(level_num="third")

    text= ("🎮 Отлично! Вы прошли второй уровень и теперь готовы к бонусному уровню, в котором познакомитесь с "
           "нестандартным применением дизайна и технологий для увеличения продаж.")
    await callback_query.message.answer(
        text=text,
        reply_markup=next_button.as_markup(resize_keyboard=True)
    )


# Third level information carousel
@third_level_router.callback_query(F.data.startswith("third_level_carousel"))
async def third_level_carousel(callback_query: CallbackQuery):
    # level = callback_query.data[:callback_query.data.find("level") + 5]

    await carousel_render(callback_query=callback_query, level_num="third")


# Third level continue
@third_level_router.callback_query(F.data == "third_level_continue")
async def third_level_continue(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    buttons = InlineKeyboardBuilder()
    buttons.add(
        InlineKeyboardButton(text="Получить задание", callback_data="third_level_task"),
        InlineKeyboardButton(text="Продолжить без бонусов", callback_data="skip_to_end")
    )

    text = "А теперь давайте закрепим информацию."

    await callback_query.message.answer(
        text=text,
        reply_markup=buttons.as_markup(resize_keyboard=True)
    )



