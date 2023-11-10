from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery

other_handler: Router = Router()


# Handler for Skip Button
@other_handler.callback_query(F.data.startswith("skip_to"))
async def skip_answer(callback_query: CallbackQuery):
    questions_dict = {"2": "second_level_intro", "3": "third_level_intro"}
    question_number = callback_query.data[-1]
    func = globals()[questions_dict[question_number]]
    await callback_query.message.answer(text="Ах как жаль :( \n")
    await func(callback_query)

