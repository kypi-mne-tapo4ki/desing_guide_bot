from aiogram import types
from aiogram.utils import keyboard

from texts.reader import read_texts

keyboards_buttons_texts = read_texts("texts/keyboards_buttons_texts.json")


async def first_page_keyboard(level_num: str):
    buttons = keyboard.InlineKeyboardBuilder()
    buttons.add(
        types.InlineKeyboardButton(
            text=keyboards_buttons_texts["forward_button_text"], callback_data=f"{level_num}_level_carousel_2"
        )
    )
    return buttons


async def middle_pages_keyboard(callback_query: types.CallbackQuery, level_num: str):
    buttons = keyboard.InlineKeyboardBuilder()
    buttons.add(
        types.InlineKeyboardButton(
            text=keyboards_buttons_texts["back_button_text"],
            callback_data=f"{level_num}_level_carousel_{(str(int(callback_query.data[-1]) - 1))}",
        ),
        types.InlineKeyboardButton(
            text=keyboards_buttons_texts["forward_button_text"],
            callback_data=f"{level_num}_level_carousel_{(str(int(callback_query.data[-1]) + 1))}",
        ),
    )
    return buttons


async def last_page_keyboard(callback_query: types.CallbackQuery, level_num: str):
    buttons = keyboard.InlineKeyboardBuilder()
    buttons.add(
        types.InlineKeyboardButton(
            text=keyboards_buttons_texts["forward_button_text"],
            callback_data=f"{level_num}_level_carousel_{(str(int(callback_query.data[-1]) - 1))}",
        ),
        types.InlineKeyboardButton(
            text=keyboards_buttons_texts["next_button_text"], callback_data=f"{level_num}_level_continue"
        ),
    )
    return buttons


async def to_carousel_keyboard(level_num: str):
    button = keyboard.InlineKeyboardBuilder()
    button.add(
        types.InlineKeyboardButton(
            text=keyboards_buttons_texts["next_button_text"],
            callback_data=f"{level_num}_level_carousel_1"
        )
    )
    return button


async def cancel_game_keyboard():
    cancel_button = keyboard.ReplyKeyboardBuilder()
    cancel_button.add(types.KeyboardButton(text=keyboards_buttons_texts["cancel_game_button_text"]))
    return cancel_button
