import asyncio
import logging
import time
from typing import Union

import pymongo

# from aiogram.utils.callback_answer import CallbackAnswerMiddleware
import aiogram.utils.keyboard as keyboard

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from config_reader import config

logging.basicConfig(level=logging.INFO)

# Bot settings
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

# DB Connection
client = pymongo.MongoClient(host=config.db_host.get_secret_value())
database = client[config.db_name.get_secret_value()]
collection = database[config.collection_name.get_secret_value()]


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "Привет и добро пожаловать! Вы попали в дизайн-игру - место, где вы сможете на практике разобраться, "
        "как графический дизайн может помочь увеличить ваши продажи и привлечь больше клиентов. А также "
        "получить скидку на мои услуги до 40%! Готовы начать свое путешествие? Давайте начнем с самых "
        "сложных вопросов!"
    )

    await message.answer(text=welcome_text, parse_mode="HTML")
    await main_menu(message)


cancel_button = keyboard.ReplyKeyboardBuilder()
cancel_button.add(types.KeyboardButton(text="Отмена игры"))


async def main_menu(message: types.Message):
    user_data = await get_user_data(message.from_user.id)

    text = "Чтобы получить бонус, нажмите 'Старт игры'"
    if user_data["discount"] != 0:
        text = (
            "Похоже вы уже играли ранее. Если начать новую игры ваши заработанные баллы сгорят. "
            "Хотите попробовать снова?\n"
        ) + text

    builder = keyboard.ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Старт игры"))

    await message.answer(
        text=text,
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(F.text == "Старт игры")
async def new_game(message: types.Message):
    await save_user_data(message.from_user.id, discount=0, user_answer="")

    await message.answer(
        text="💡 Уровень 1: Зачем нужен графический дизайн? Бонус за прохождение: скидка 10%",
        reply_markup=cancel_button.as_markup(resize_keyboard=True),
    )

    next_button = keyboard.InlineKeyboardBuilder()
    next_button.add(
        types.InlineKeyboardButton(text="Далее", callback_data="first_question")
    )

    introduction_text = (
        "Перед тем как перейти к первому вопросу, давайте разберемся, почему графический дизайн так важен:"
        "\n👁️ Привлекательность: Привлекательный дизайн делает ваш продукт или услугу более заметными и привлекательными"
        "для потенциальных клиентов. Это первое, что они видят."
        "\n🧠 Понимание: Графика помогает объяснить, как работает ваш продукт и какие преимущества он предоставляет."
        "Это помогает клиентам понять, как ваш продукт решает их проблемы."
        "\n🤝 Доверие: Профессиональный дизайн создает впечатление надежности и качества. Это может помочь убедить "
        "клиентов, что они делают правильный выбор."
    )

    await message.answer(
        text=introduction_text, reply_markup=next_button.as_markup(resize_keybord=True)
    )


@dp.callback_query(F.data == "first_question")
async def first_question_handle(callback_query: types.CallbackQuery):
    # Hide inline button from previous message
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=callback_query.message.text,
        reply_markup=None,  # Hide keyboard
    )

    await callback_query.message.answer(
        text="Для получения бонуса, ответьте на вопрос:",
        reply_markup=cancel_button.as_markup(resize_keyboard=True),
    )

    first_question_buttons = keyboard.InlineKeyboardBuilder()
    first_question_buttons.add(
        types.InlineKeyboardButton(text="Ответить", callback_data="first_answer")
    )
    first_question_buttons.add(
        types.InlineKeyboardButton(
            text="Продолжить без бонуса", callback_data="cancel_answer"
        )
    )

    question_one_text = (
        "🤔Вопрос: А что делает ваш продукт или услугу более заметными и привлекательными"
        " для потенциальных клиентов?"
    )

    await callback_query.message.answer(
        text=question_one_text,
        reply_markup=first_question_buttons.as_markup(resize_keyboard=True),
    )


@dp.callback_query(F.data == "first_answer")
async def first_answer(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Напишите свой ответ")

    @dp.message(F.text)
    async def get_answer(message: types.Message):
        print(message.text)
        await save_user_data(
            user_id=message.from_user.id, discount=10, user_answer=message.text
        )

        next_button = keyboard.InlineKeyboardBuilder()
        next_button.add(
            types.InlineKeyboardButton(text="Далее", callback_data="second_question")
        )

        text = (
            "🎮 Отлично! Ваши знания о графическом дизайне и его влиянии на бизнес продолжают расти. "
            "Готовы к следующему вызову?"
        )
        await message.answer(
            text=text, reply_markup=next_button.as_markup(resize_keyboard=True)
        )


@dp.callback_query(F.data == "second_question")
async def second_question(callback_query: types.CallbackQuery):
    # Hide inline button from previous message
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=callback_query.message.text,
        reply_markup=None,  # Hide keyboard
    )

    introdution_text = (
        "🌟 Уровень 2: Как можно увеличить продажи с помощью дизайна?"
        "Бонус за прохождение уровня: скидка +10%"
        "Теперь давайте перейдем к методам увеличения продаж с помощью графики:"
    )

    await callback_query.message.answer(
        text=introdution_text,
        reply_markup=cancel_button.as_markup(resize_keyboard=True),
    )


@dp.message(F.text == "Отмена игры")
async def handle_cancel_game(message: types.Message):
    # Завершите игру и вернитесь в основное меню
    await bot.send_message(
        chat_id=message.chat.id,
        text="Игра завершена. Вернемся в основное меню.",
    )
    await main_menu(message)


# Функции для сохранения и извлечения данных из базы данных
async def save_user_data(user_id, discount, user_answer):
    data = {"user_id": user_id, "discount": discount, "user_answer": user_answer}
    collection.update_one({"user_id": user_id}, {"$set": data}, upsert=True)


async def get_user_data(user_id):
    user_data = collection.find_one({"user_id": user_id})
    if user_data:
        discount = user_data.get("discount", 0)
        user_answer = user_data.get("user_answer", "")
        return {"discount": discount, "user_answer": user_answer}
    else:
        return {"discount": 0, "user_answer": ""}


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
