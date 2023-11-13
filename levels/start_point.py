import aiogram
from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, InlineKeyboardButton

from models.users import User, update_user_data, get_user_data, clear_user_data

start_point_router: Router = Router()


@start_point_router.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        "Привет и добро пожаловать! Вы попали в дизайн-игру - место, где вы сможете на практике разобраться, "
        "как графический дизайн может помочь увеличить ваши продажи и привлечь больше клиентов. А также "
        "получить скидку на мои услуги до 40%! Готовы начать свое путешествие? Давайте начнем с самых "
        "сложных вопросов!"
    )

    await message.answer(text=welcome_text)
    await main_menu(message=message)


async def main_menu(message: Message):
    user = await get_user_data(message.from_user.id)

    text = "Чтобы получить бонус, нажмите 'Старт игры'"
    if user:
        user_data = user.to_dict()
        text = (
                   f"Похоже ты уже играл ранее. \nТвоя накопленная скидка <b>{user_data['discount']}%</b>. "
                   "Если начать новую игры ваши заработанные баллы сгорят. "
                   "Хотите попробовать снова?\n\n"
               ) + text
    else:
        user = User(user_id=message.from_user.id, username=message.from_user.username)
        await user.save()

    start_button = ReplyKeyboardBuilder()
    start_button.add(KeyboardButton(text="Старт игры"))

    await message.answer(
        text=text,
        reply_markup=start_button.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )


# Start game
@start_point_router.message(F.text == "Старт игры")
async def new_game(message: Message):
    # Clear user data
    await clear_user_data(user_id=message.from_user.id, username=message.from_user.username)

    next_button = InlineKeyboardBuilder()
    next_button.add(
        InlineKeyboardButton(text="Далее", callback_data="first_level")
    )

    await message.answer(
        text="Желаю удачи!",
        reply_markup=next_button.as_markup(resize_keyboard=True)
    )
