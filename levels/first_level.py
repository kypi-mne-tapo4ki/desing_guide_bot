from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from keyboards import cancel_game_keyboard, to_carousel_keyboard
from models.users import clear_user_data, increment_discount, update_user_data, get_user_data
from tools import carousel_render, hide_buttons, read_texts

first_level_router: Router = Router()
start_point_texts = read_texts("texts/start_point_texts.json")
first_level_texts = read_texts("texts/first_level_texts.json")


# First level
@first_level_router.message(F.text.startswith(start_point_texts["start_button_text"]))
async def first_level_intro(message: Message):
    await clear_user_data(
        user_id=message.from_user.id, username=message.from_user.username
    )

    next_button = await to_carousel_keyboard(level_num="first")

    level_text = first_level_texts["level_text"]
    cancel_game_button = await cancel_game_keyboard()

    await message.answer(
        text=level_text,
        reply_markup=cancel_game_button.as_markup(resize_keyboard=True),
        parse_mode="HTML",
    )

    next_text = first_level_texts["next_text"]
    await message.answer(
        text=next_text,
        reply_markup=next_button.as_markup(resize_keyboard=True),
        parse_mode="HTML",
    )


# First level information carousel
@first_level_router.callback_query(F.data.startswith("first_level_carousel"))
async def first_level_carousel(callback_query: CallbackQuery):
    await carousel_render(callback_query=callback_query, level_num="first")


# First level continue
@first_level_router.callback_query(F.data == "first_level_continue")
async def first_level_continue(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    await callback_query.message.answer(text=first_level_texts["instruction_text"])

    first_question_buttons = InlineKeyboardBuilder()
    first_question_buttons.add(
        InlineKeyboardButton(text=first_level_texts["answer_button_text"], callback_data="first_level_task"),
        InlineKeyboardButton(text=first_level_texts["without_bonus_button_text"], callback_data="skip_to_2"),
    )
    first_question_buttons.adjust(1)
    first_question_text = first_level_texts["first_question_text"]

    await callback_query.message.answer(
        text=first_question_text,
        reply_markup=first_question_buttons.as_markup(resize_keyboard=True),
    )


# First level task
@first_level_router.callback_query(F.data == "first_level_task")
async def first_answer_handler(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    recommendation_text = first_level_texts["recommendation_text"]
    await callback_query.message.answer(text=recommendation_text, parse_mode="HTML")


@first_level_router.message(
    F.text.upper().startswith(first_level_texts["first_filter_text"]) | F.text.upper().startswith("second_filter_text")
)
async def get_answer(message: Message):
    user = await get_user_data(user_id=message.from_user.id)
    if user.utp is None:
        await update_user_data(user_id=user.user_id, utp=message.text)
        await increment_discount(user_id=user.user_id)

        next_button = InlineKeyboardBuilder()
        next_button.add(
            InlineKeyboardButton(text=first_level_texts["next_button_text"], callback_data="second_level_intro")
        )
        congrats_text = first_level_texts["congrats_text"]

        await message.answer(
            text=congrats_text, reply_markup=next_button.as_markup(resize_keyboard=True)
        )
    else:
        ok_button = InlineKeyboardBuilder()
        ok_button.add(
            InlineKeyboardButton(text=first_level_texts["ok_button_text"], callback_data="second_level_intro")
        )
        angry_text = first_level_texts["angry_text"]

        await message.answer(
            text=angry_text,
            reply_markup=ok_button.as_markup(resize_keyboard=True)
    )
