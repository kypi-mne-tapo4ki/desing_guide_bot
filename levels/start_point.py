from datetime import datetime

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from models.users import User, get_user_data
from tools import read_texts

start_point_router: Router = Router()
start_point_texts = read_texts("texts/start_point_texts.json")


@start_point_router.message(Command("start"))
async def cmd_start(message: Message):
    user = await get_user_data(message.chat.id)

    basic_text = start_point_texts["basic_text"]
    game_already_played_text = start_point_texts["game_already_played_text"]
    start_button_text = start_point_texts["start_button_text"]

    message_text = basic_text
    if user and user.discount != 0:
        message_text = game_already_played_text.format(discount=user.discount) + message_text
    else:
        user = User(user_id=message.from_user.id, username=message.from_user.username, date=datetime.utcnow())
        await user.save()

    start_button = ReplyKeyboardBuilder()
    start_button.add(KeyboardButton(text=start_button_text))

    await message.answer(
        text=message_text,
        reply_markup=start_button.as_markup(resize_keyboard=True),
        parse_mode="HTML",
    )
