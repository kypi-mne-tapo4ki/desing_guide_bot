from aiogram.utils import keyboard
from aiogram import types


async def first_page_keyboard(level: str):
    buttons = keyboard.InlineKeyboardBuilder()
    buttons.add(
        types.InlineKeyboardButton(text=">>>", callback_data=f"{level}_carousel_2")
    )
    return buttons


async def middle_pages_keyboard(callback_query: types.CallbackQuery, level: str):
    buttons = keyboard.InlineKeyboardBuilder()
    buttons.add(
        types.InlineKeyboardButton(text="<<<",
                                   callback_data=f"{level}_carousel_{(str(int(callback_query.data[-1]) - 1))}"),
        types.InlineKeyboardButton(text=">>>",
                                   callback_data=f"{level}_carousel_{(str(int(callback_query.data[-1]) + 1))}"),
    )
    return buttons


async def last_page_keyboard(callback_query: types.CallbackQuery, level: str):
    buttons = keyboard.InlineKeyboardBuilder()
    buttons.add(
        types.InlineKeyboardButton(text="<<<",
                                   callback_data=f"{level}_carousel_{(str(int(callback_query.data[-1]) - 1))}"),
        types.InlineKeyboardButton(text="Далее", callback_data=f"{level}_continue")
    )
    return buttons


async def to_carousel_keyboard(level: str):
    button = keyboard.InlineKeyboardBuilder()
    button.add(
        types.InlineKeyboardButton(text="Далее", callback_data=f"{level}_carousel_1")
    )
    return button


async def cancel_game_keyboard():
    cancel_button = keyboard.ReplyKeyboardBuilder()
    cancel_button.add(types.KeyboardButton(text="Отмена игры"))
    return cancel_button
