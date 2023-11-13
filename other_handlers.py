from aiogram import F, Router
from aiogram.types import CallbackQuery

from levels.second_level import second_level_intro
from levels.third_level import third_level_intro
from levels.end_point import finish_game

other_handlers: Router = Router()


# Handler for Skip Button
@other_handlers.callback_query(F.data.startswith("skip_to"))
async def skip_answer(callback_query: CallbackQuery):
    levels_dict = {
        "2": "second_level_intro",
        "3": "third_level_intro",
        "end": "finish_game",
    }
    level = callback_query.data[8:]
    func = globals()[levels_dict[level]]
    await callback_query.message.answer(text="Ах как жаль :( \n")
    await func(callback_query)
