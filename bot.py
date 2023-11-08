import asyncio
import logging
import time

import pymongo

import aiogram.utils.keyboard as keyboard
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command

import data as d
from config_reader import config

logging.basicConfig(level=logging.INFO)

# Bot settings
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

# DB Connection
client = pymongo.MongoClient(host=config.db_host.get_secret_value())
database = client[config.db_name.get_secret_value()]
collection = database[config.collection_name.get_secret_value()]


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

    start_button = keyboard.ReplyKeyboardBuilder()
    start_button.add(types.KeyboardButton(text="Старт игры"))

    await message.answer(
        text=text,
        reply_markup=start_button.as_markup(resize_keyboard=True),
    )


# Start Game
@dp.message(F.text == "Старт игры")
async def new_game(message: types.Message):
    await save_user_data(message.from_user.id, discount=0, user_answer="")

    next_button = keyboard.InlineKeyboardBuilder()
    next_button.add(
        types.InlineKeyboardButton(text="Далее", callback_data="first_level")
    )

    await message.answer(
        text="Желаю удачи!",
        reply_markup=next_button.as_markup(resize_keyboard=True)
    )


# First Level
@dp.callback_query(F.data == "first_level")
async def first_level_intro(callback_query: types.CallbackQuery):
    # Hide inline button from previous message
    await hide_buttons(callback_query=callback_query)

    next_button = await to_carousel_keyboard(level="first_level")

    text = ("💡 Уровень 1: Зачем нужен графический дизайн? Бонус за прохождение: скидка 10%"
            " Перед тем как перейти к первому вопросу, давайте разберемся, почему графический дизайн так важен:"
            )
    await callback_query.message.answer(text=text)

    time.sleep(2)

    await callback_query.message.answer(
        text="Нажмите Далее",
        reply_markup=next_button.as_markup(resize_keyboard=True)
    )


@dp.callback_query(F.data.startswith("first_level_carousel"))
async def first_level_carousel(callback_query: types.CallbackQuery):
    # Hide inline button from previous message
    await hide_buttons(callback_query=callback_query)

    data = await d.get_first_level_data()
    level = callback_query.data[:callback_query.data.find("level") + 5]
    carousel_number = callback_query.data[-1]
    middle_list = [str(i) for i in range(2, 3)]

    if carousel_number == "1":
        page_keyboard = await first_page_keyboard(level=level)
        await edit_carousel_message(
            callback_query=callback_query,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )

    elif carousel_number in middle_list:
        page_keyboard = await middle_pages_keyboard(callback_query=callback_query, level=level)
        await edit_carousel_message(
            callback_query=callback_query,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )

    elif carousel_number == str(len(data)):
        page_keyboard = await last_page_keyboard(callback_query=callback_query, level=level)
        await edit_carousel_message(
            callback_query=callback_query,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )


@dp.callback_query(F.data == "first_level_continue")
async def first_level_continue(callback_query: types.CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    await callback_query.message.answer(
        text="Для получения бонуса, ответьте на вопрос:",
        reply_markup=cancel_button.as_markup(resize_keyboard=True),
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


# First Answer
@dp.callback_query(F.data == "first_level_task")
async def first_answer(callback_query: types.CallbackQuery):
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


# Second Question
@dp.callback_query(F.data == "second_level_intro")
async def second_level_intro(callback_query: types.CallbackQuery):
    # Hide inline button from previous message
    await hide_buttons(callback_query=callback_query)

    introdution_text = (
        "🌟 Уровень 2: Как можно увеличить продажи с помощью дизайна?"
        "Бонус за прохождение уровня: скидка +10%"
    )

    await callback_query.message.answer(
        text=introdution_text,
        reply_markup=cancel_button.as_markup(resize_keyboard=True),
    )

    next_button = await to_carousel_keyboard(level="second_level")

    await callback_query.message.answer(
        text="Теперь давайте перейдем к методам увеличения продаж с помощью графики:",
        reply_markup=next_button.as_markup(resize_keyboard=True),
    )


@dp.callback_query(F.data.startswith("second_level_carousel"))
async def second_part_carousel(callback_query: types.CallbackQuery):
    await hide_buttons(callback_query)

    data = await d.get_second_level_data()
    level = callback_query.data[:callback_query.data.find("level") + 5]
    carousel_number = callback_query.data[-1]
    middle_list = [str(i) for i in range(2, 6)]

    await callback_query.answer(text=" ")

    # if carousel_number == "1":
    #     await bot.edit_message_text(
    #         chat_id=callback_query.message.chat.id,
    #         message_id=callback_query.message.message_id,
    #         text=data[carousel_number],
    #         reply_markup=buttons_for_first.as_markup(reply_keyboard=True)
    #     )
    #
    # elif carousel_number in middle_list:
    #     await bot.edit_message_text(
    #         chat_id=callback_query.message.chat.id,
    #         message_id=callback_query.message.message_id,
    #         text=data[carousel_number],
    #         reply_markup=buttons_for_middle.as_markup(reply_keyboard=True)
    #     )
    #
    # elif carousel_number == "6":
    #     await bot.edit_message_text(
    #         chat_id=callback_query.message.chat.id,
    #         message_id=callback_query.message.message_id,
    #         text=data[carousel_number],
    #         reply_markup=buttons_for_last.as_markup(reply_keyboard=True)
    #     )
    if carousel_number == "1":
        page_keyboard = await first_page_keyboard(level=level)
        await edit_carousel_message(
            callback_query=callback_query,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )

    elif carousel_number in middle_list:
        page_keyboard = await middle_pages_keyboard(callback_query=callback_query, level=level)
        await edit_carousel_message(
            callback_query=callback_query,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )

    elif carousel_number == str(len(data)):
        page_keyboard = await last_page_keyboard(callback_query=callback_query, level=level)
        await edit_carousel_message(
            callback_query=callback_query,
            page_keyboard=page_keyboard,
            page_text=data[carousel_number]
        )


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


@dp.callback_query(F.data == "second_level_task")
async def second_task(callback_query: types.CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    await callback_query.message.answer("Мы здесь")


@dp.callback_query(F.data == "third_level_intro")
async def third_level_intro(callback_query: types.CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    await callback_query.message.answer("Перешли на третий уровень")


@dp.callback_query(F.data.startswith("skip_to"))
async def skip_answer(callback_query: types.CallbackQuery):
    questions_dict = {"2": "second_level_intro", "3": "third_level_intro"}
    question_number = callback_query.data[-1]
    func = globals()[questions_dict[question_number]]
    await callback_query.message.answer(text="Ах как жаль :( \n")
    await func(callback_query)


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


async def hide_buttons(callback_query: types.CallbackQuery):
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=callback_query.message.text,
        reply_markup=None,  # Hide keyboard
    )


async def edit_carousel_message(
        callback_query: types.CallbackQuery,
        page_keyboard: keyboard.InlineKeyboardBuilder,
        page_text: str,
):
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=page_text,
        reply_markup=page_keyboard.as_markup(resize_keyboard=True)
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
