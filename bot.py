import asyncio
import logging
import random

import pymongo

import aiogram.utils.keyboard as keyboard
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command

import data
from data import get_first_level_data, get_second_level_data
from config_reader import config
from keyboards import (
    first_page_keyboard,
    middle_pages_keyboard,
    last_page_keyboard,
    to_carousel_keyboard,
    cancel_game_keyboard
)

logging.basicConfig(level=logging.INFO)

# Bot settings
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

# DB connection
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


async def main_menu(message: types.Message):
    user_data = await get_user_data(message.from_user.id)

    text = "Чтобы получить бонус, нажмите 'Старт игры'"
    if user_data["discount"] != 0:
        text = (
                   "Похоже вы уже играли ранее. Если начать новую игры ваши заработанные баллы сгорят. "
                   "Хотите попробовать снова?\n"
               ) + text

    start_button = keyboard.ReplyKeyboardBuilder()
    start_button.add(types.KeyboardButton(text="Старт игры"))

    await message.answer(
        text=text,
        reply_markup=start_button.as_markup(resize_keyboard=True),
    )


# Start game
@dp.message(F.text == "Старт игры")
async def new_game(message: types.Message):
    # Init and clear user data
    await save_user_data(message.from_user.id, discount=0, user_answer="")

    next_button = keyboard.InlineKeyboardBuilder()
    next_button.add(
        types.InlineKeyboardButton(text="Далее", callback_data="first_level")
    )

    await message.answer(
        text="Желаю удачи!",
        reply_markup=next_button.as_markup(resize_keyboard=True)
    )


# First level
@dp.callback_query(F.data == "first_level")
async def first_level_intro(callback_query: types.CallbackQuery):
    # Hide inline button from previous message
    await hide_buttons(callback_query=callback_query)

    next_button = await to_carousel_keyboard(level="first_level")

    level_text = "💡 Уровень 1: Зачем нужен графический дизайн? Бонус за прохождение: скидка 10%"
    cancel_game_button = await cancel_game_keyboard()

    await callback_query.message.answer(
        text=level_text,
        reply_markup=cancel_game_button.as_markup(resize_keyboard=True)
    )

    next_text = " Перед тем как перейти к первому вопросу, давайте разберемся, почему графический дизайн так важен:"
    await callback_query.message.answer(
        text=next_text,
        reply_markup=next_button.as_markup(resize_keyboard=True),
    )


# First level information carousel
@dp.callback_query(F.data.startswith("first_level_carousel"))
async def first_level_carousel(callback_query: types.CallbackQuery):
    level = callback_query.data[:callback_query.data.find("level") + 5]

    await carousel_render(callback_query=callback_query, level=level)


# First level continue
@dp.callback_query(F.data == "first_level_continue")
async def first_level_continue(callback_query: types.CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    cancel_game_button = await cancel_game_keyboard()
    await callback_query.message.answer(
        text="Для получения бонуса, ответьте на вопрос:",
        reply_markup=cancel_game_button.as_markup(resize_keyboard=True),
    )

    first_question_buttons = keyboard.InlineKeyboardBuilder()
    first_question_buttons.add(
        types.InlineKeyboardButton(text="Ответить", callback_data="first_level_task")
    )
    first_question_buttons.add(
        types.InlineKeyboardButton(
            text="Продолжить без бонуса", callback_data="skip_to_2"
        )
    )

    first_question_text = (
        "🤔Вопрос: А что делает ваш продукт или услугу более заметными и привлекательными"
        " для потенциальных клиентов?"
    )

    await callback_query.message.answer(
        text=first_question_text,
        reply_markup=first_question_buttons.as_markup(resize_keyboard=True),
    )


# First level task
@dp.callback_query(F.data == "first_level_task")
async def first_answer_handler(callback_query: types.CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    await callback_query.message.answer("Напишите свой ответ")

    @dp.message(F.text)
    async def get_answer(message: types.Message):
        await save_user_data(
            user_id=message.from_user.id, discount=10, user_answer=message.text
        )

        next_button = keyboard.InlineKeyboardBuilder()
        next_button.add(
            types.InlineKeyboardButton(text="Далее", callback_data="second_level_intro")
        )

        text = (
            "🎮 Отлично! Ваши знания о графическом дизайне и его влиянии на бизнес продолжают расти. "
            "Готовы к следующему вызову?"
        )
        await message.answer(
            text=text, reply_markup=next_button.as_markup(resize_keyboard=True)
        )


# Second level
@dp.callback_query(F.data == "second_level_intro")
async def second_level_intro(callback_query: types.CallbackQuery):
    # Hide inline button from previous message
    await hide_buttons(callback_query=callback_query)

    introdution_text = (
        "🌟 Уровень 2: Как можно увеличить продажи с помощью дизайна?"
        "Бонус за прохождение уровня: скидка +10% или +20%"
    )

    cancel_game_button = await cancel_game_keyboard()
    await callback_query.message.answer(
        text=introdution_text,
        reply_markup=cancel_game_button.as_markup(resize_keyboard=True),
    )

    next_button = await to_carousel_keyboard(level="second_level")

    await callback_query.message.answer(
        text="Теперь давайте перейдем к методам увеличения продаж с помощью графики:",
        reply_markup=next_button.as_markup(resize_keyboard=True),
    )


# Second level information carousel
@dp.callback_query(F.data.startswith("second_level_carousel"))
async def second_level_carousel(callback_query: types.CallbackQuery):
    level = callback_query.data[:callback_query.data.find("level") + 5]

    await carousel_render(callback_query=callback_query, level=level)


# Second level continue
@dp.callback_query(F.data == "second_level_continue")
async def second_level_continue(callback_query: types.CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    buttons = keyboard.InlineKeyboardBuilder()
    buttons.add(
        types.InlineKeyboardButton(text="Получить задание", callback_data="second_level_task"),
        types.InlineKeyboardButton(text="Продолжить без бонусов", callback_data="skip_to_3")
    )

    text = "Перед тем как идти дальше, давайте закрепим информацию на примерах."
    await callback_query.message.answer(
        text=text,
        reply_markup=buttons.as_markup(resize_keyboard=True)
    )


# Second level task
@dp.callback_query(F.data == "second_level_task")
async def second_level_task_info(callback_query: types.CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    task_text = "Задание: Сопоставьте бренд и его описание"

    origin_results = await data.get_second_level_answers()
    user_results = {}
    button = keyboard.InlineKeyboardBuilder()
    button.add(types.InlineKeyboardButton(text="Вперед", callback_data="answer_"))

    await callback_query.message.answer(
        text=task_text,
        reply_markup=button.as_markup(reply_keyboard=True)
    )

    @dp.callback_query(F.data.startswith("answer_"))
    async def second_level_answers(callback_query_a: types.CallbackQuery):

        current_answer: str = ""

        try:
            current_answer = callback_query_a.data.split("_")[1]
            origin_results.pop(current_answer)
        except (KeyError, IndexError):
            pass

        if current_answer != "":
            user_results.update({current_answer: callback_query_a.message.text})

            await bot.edit_message_text(
                chat_id=callback_query_a.message.chat.id,
                message_id=callback_query_a.message.message_id,
                text=callback_query_a.message.text + f"\nВаш ответ: {current_answer}"
            )
        else:
            await hide_buttons(callback_query=callback_query_a)

        if len(origin_results) == 0:
            await hide_buttons(callback_query=callback_query_a)
            await second_level_check_result(
                callback_query=callback_query_a,
                user_results=user_results
            )

        answers_keyboard = keyboard.InlineKeyboardBuilder()
        for key in origin_results.keys():
            answers_keyboard.add(types.InlineKeyboardButton(text=key, callback_data=f"answer_{key}"))
        answers_keyboard.adjust(2)

        answer, text = random.sample(origin_results.items(), 1)[0]

        await callback_query_a.message.answer(
            text=text,
            reply_markup=answers_keyboard.as_markup(resize_keyboard=True)
        )


# Second level result checking
async def second_level_check_result(callback_query: types.CallbackQuery, user_results: dict):
    origin_results = await data.get_second_level_answers()
    if user_results == origin_results:
        user_data = await get_user_data(callback_query.message.from_user.id)
        user_data["discount"] = user_data.get("discount", 0) + 10
        await save_user_data(**user_data)

        text="Поздравляю! Ты ответил правильно, держи 10% скидки 🥳. Ты можешь получить еще 10% если ответишь на бонусный вопрос"
        buttons = keyboard.InlineKeyboardBuilder()
        buttons.add(
            types.InlineKeyboardButton(text="Получить бонус", callback_data="bonus_task"),
            types.InlineKeyboardButton(text="Продолжить без бонуса", callback_data="skip_to_3"),
        )

        await callback_query.message.answer(
            text=text,
            reply_markup=buttons.as_markup(resize_keyboard=True)
        )
    else:
        buttons = keyboard.InlineKeyboardBuilder()
        buttons.add(
            types.InlineKeyboardButton(text="Попробовать снова", callback_data="second_level_task"),
            types.InlineKeyboardButton(text="Получить бонус", callback_data="bonus_task"),
            types.InlineKeyboardButton(text="Продолжить без бонуса", callback_data="skip_to_3"),
        )
        buttons.adjust(1)

        text = ("Извини, но ты ответил неверно. Ты можешь попробовать пройти задание снова, либо получить "
                "10% скидку ответив на бонусный вопрос или продолжить без бонусов. Выбирай:")

        await callback_query.message.answer(
            text=text,
            reply_markup=buttons.as_markup(resize_keyboard=True)
        )


# Second level bonus task
@dp.callback_query(F.data == "bonus_task")
async def bonus_task(callback_query: types.CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    text = "Бонусное задание - напишите, какие плюсы и минусы вы заметили у своей компании?"
    await callback_query.message.answer(text=text)

    @dp.message(F.text)
    async def get_answer(message: types.Message):
        await update_user_discount(message.from_user.id)

        next_button = keyboard.InlineKeyboardBuilder()
        next_button.add(
            types.InlineKeyboardButton(text="Далее", callback_data="third_level_intro")
        )

        text = (
            "🎮 Отлично! Ваши знания о графическом дизайне и его влиянии на бизнес продолжают расти. "
            "Готовы к следующему вызову?"
        )
        await message.answer(
            text=text, reply_markup=next_button.as_markup(resize_keyboard=True)
        )


# Third level
@dp.callback_query(F.data == "third_level_intro")
async def third_level_intro(callback_query: types.CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    await callback_query.message.answer("Перешли на третий уровень")


# Handler for Skip Button
@dp.callback_query(F.data.startswith("skip_to"))
async def skip_answer(callback_query: types.CallbackQuery):
    questions_dict = {"2": "second_level_intro", "3": "third_level_intro"}
    question_number = callback_query.data[-1]
    func = globals()[questions_dict[question_number]]
    await callback_query.message.answer(text="Ах как жаль :( \n")
    await func(callback_query)


# Event to cancel the game
@dp.message(F.text == "Отмена игры")
async def handle_cancel_game(message: types.Message):
    # Завершите игру и вернитесь в основное меню
    await bot.send_message(
        chat_id=message.chat.id,
        text="Игра завершена. Вернемся в основное меню.",
    )
    await main_menu(message)


# The following two functions are for saving and retrieving data from the database
async def save_user_data(user_id, discount, user_answer):
    data = {"user_id": user_id, "discount": discount, "user_answer": user_answer}
    collection.update_one({"user_id": user_id}, {"$set": data}, upsert=True)


async def get_user_data(user_id):
    user_data = collection.find_one({"user_id": user_id})
    if user_data:
        discount = user_data.get("discount", 0)
        user_answer = user_data.get("user_answer", "")
        return {"discount": discount, "user_answer": user_answer, "user_id": user_id}
    else:
        return {"discount": 0, "user_answer": "", "user_id": user_id}


async def update_user_discount(user_id):
    user_data = await get_user_data(user_id)
    user_data["discount"] = user_data.get("discount", 0) + 10
    await save_user_data(**user_data)


# This function draws a carousel for a given level
async def carousel_render(
        callback_query: types.CallbackQuery,
        level: str
):
    # Hide inline button from previous message
    await hide_buttons(callback_query=callback_query)

    levels_data = {"first_level": "get_first_level_data", "second_level": "get_second_level_data"}
    func = globals()[levels_data[level]]
    data = await func()
    carousel_number = callback_query.data[-1]
    middle_list = [str(i) for i in range(2, len(data))]
    message_id = callback_query.message.message_id

    if callback_query.message.text not in data.values():
        temp = await callback_query.message.answer(text="Загрузка...")
        message_id = temp.message_id

    if carousel_number == "1":
        page_keyboard = await first_page_keyboard(level=level)
        await edit_carousel_message(
            callback_query=callback_query,
            message_id=message_id,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )

    elif carousel_number in middle_list:
        page_keyboard = await middle_pages_keyboard(callback_query=callback_query, level=level)
        await edit_carousel_message(
            callback_query=callback_query,
            message_id=message_id,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )

    elif carousel_number == str(len(data)):
        page_keyboard = await last_page_keyboard(callback_query=callback_query, level=level)
        await edit_carousel_message(
            callback_query=callback_query,
            message_id=message_id,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )


async def edit_carousel_message(
        callback_query: types.CallbackQuery,
        message_id: int,
        page_keyboard: keyboard.InlineKeyboardBuilder,
        page_text: str,
):
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=message_id,
        text=page_text,
        reply_markup=page_keyboard.as_markup(resize_keyboard=True)
    )


# It`s hides previous message`s buttons
async def hide_buttons(callback_query: types.CallbackQuery):
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=callback_query.message.text,
        reply_markup=None,  # Hide keyboard
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
