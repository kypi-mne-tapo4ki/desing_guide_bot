from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from bot import bot
from levels.start_point import main_menu

end_point_router: Router = Router()


@end_point_router.callback_query(F.text == "end_point_intro")
async def end_point_intro(callback_query: CallbackQuery):
    pass


# Event to end the game
@end_point_router.message(F.text == "Отмена игры")
async def finish_game(message: Message):
    # Завершите игру и вернитесь в основное меню
    await bot.send_message(
        chat_id=message.chat.id,
        text="Игра завершена. Вернемся в основное меню.",
    )
    await main_menu(message)

