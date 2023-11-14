from datetime import datetime

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from models.users import User, get_user_data

start_point_router: Router = Router()


@start_point_router.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        "Привет и добро пожаловать! Ты попал в дизайн-игру - место, где ты сможешь на практике разобраться, "
        "как графический дизайн может помочь увеличить твои продажи и привлечь больше клиентов. А также "
        "получить скидку на мои услуги до <b>40%</b>! Готов начать свое путешествие? Давай начнем с самых "
        "сложных вопросов!"
    )

    await message.answer(text=welcome_text, parse_mode="HTML")
    await main_menu(message=message)


async def main_menu(message: Message):
    user = await get_user_data(message.chat.id)

    text = 'Чтобы начать, нажми "<b>Старт игры</b>"'
    if user:
        text = (
            "Похоже ты уже играл ранее. \nЕсли начать новую игру, твой результат <b>обнулится</b>. Ты можешь написать "
            f"мне @theermolaeva, чтобы получить скидку <b>{user.discount}%</b> на услуги графического дизайнера или"
            " попробовать пройти игру занова.\n\n"
        ) + text
    else:
        user = User(user_id=message.from_user.id, username=message.from_user.username, date=datetime.utcnow())
        await user.save()

    start_button = ReplyKeyboardBuilder()
    start_button.add(KeyboardButton(text="Старт игры"))

    await message.answer(
        text=text,
        reply_markup=start_button.as_markup(resize_keyboard=True),
        parse_mode="HTML",
    )
