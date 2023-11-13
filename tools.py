from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data import get_first_level_data, get_second_level_data, get_third_level_data

from bot import bot
from keyboards import first_page_keyboard, middle_pages_keyboard, last_page_keyboard


# This function draws a carousel for a given level
async def carousel_render(
        callback_query: CallbackQuery,
        level_num: str
):
    # Hide inline button from previous message
    await hide_buttons(callback_query=callback_query)

    levels_data = {
        "first": "get_first_level_data",
        "second": "get_second_level_data",
        "third": "get_third_level_data",
    }
    func = globals()[levels_data[level_num]]
    data = await func()
    carousel_number = callback_query.data[-1]
    middle_list = [str(i) for i in range(2, len(data))]
    message_id = callback_query.message.message_id

    if callback_query.message.text not in data.values():
        temp = await callback_query.message.answer(text="Загрузка...")
        message_id = temp.message_id

    if carousel_number == "1":
        page_keyboard = await first_page_keyboard(level_num=level_num)
        await edit_carousel_message(
            callback_query=callback_query,
            message_id=message_id,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )

    elif carousel_number in middle_list:
        page_keyboard = await middle_pages_keyboard(callback_query=callback_query, level_num=level_num)
        await edit_carousel_message(
            callback_query=callback_query,
            message_id=message_id,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )

    elif carousel_number == str(len(data)):
        page_keyboard = await last_page_keyboard(callback_query=callback_query, level_num=level_num)
        await edit_carousel_message(
            callback_query=callback_query,
            message_id=message_id,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )


async def edit_carousel_message(
        callback_query: CallbackQuery,
        message_id: int,
        page_keyboard: InlineKeyboardBuilder,
        page_text: str,
):
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=message_id,
        text=page_text,
        reply_markup=page_keyboard.as_markup(resize_keyboard=True)
    )


# It`s hides previous message`s buttons
async def hide_buttons(callback_query: CallbackQuery):
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=callback_query.message.text,
        reply_markup=None,  # Hide keyboard
    )


async def add_user_answer(callback_query: CallbackQuery, current_answer: str):
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=callback_query.message.text + f"\nВаш ответ: <b>{current_answer}</b>",
        parse_mode="HTML"
    )
