from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import bot
from config_reader import config
from levels.start_point import main_menu
from models.users import get_user_data
from tools import hide_buttons

end_point_router: Router = Router()


@end_point_router.callback_query(F.text == "end_point_intro")
async def end_point_intro(callback_query: CallbackQuery):
    await callback_query.message.answer(text="ОК! Теперь настало время применить полученные знания на практике 😉")

    buttons = InlineKeyboardBuilder()
    buttons.add(
        InlineKeyboardButton(text="Использовать бонус!", callback_data="use_discount"),
        InlineKeyboardButton(text="Отложить бонус", callback_data="postpone_discount"),
    )
    buttons.adjust(1)

    text = (
        'Если ты готов использовать свой бонус - нажми на кнопку "Использовать бонус!" - и я свяжусь с тобой в '
        'ближайшее время. Также ты можете написать мне самостоятельно @theermolaeva. '
        'Чтобы воспользоваться скидкой в другой раз, нажми на кнопку "Отложить бонус" и я сохраню ее для тебя в '
        'течение года. \n\nЕсли тебе понравилась игра - отмечай меня в @ и делись со своими друзьями! Желаю тебе '
        'хорошего дня и очереди из клиентов 😉'
    )

    await callback_query.message.answer(
        text=text,
        reply_markup=buttons.as_markup(resize_keyboard=True),
    )


@end_point_router.callback_query(F.text == "use_discount")
async def use_discount(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    await callback_query.message.answer("Спасибо за за игру! Возвращаю вас в главное меню. Chao!")

    admin = int(config.admin_id.get_secret_value())
    user = await get_user_data(user_id=callback_query.message.chat.id)

    text = (f"Новая заявка от пользователя @{user.username} "
            f"\nСкидка: <b>{user.discount}%</b> \nUTP: {user.utp} \nPain: {user.pain}")
    await bot.send_message(
        chat_id=admin,
        text=text,
        parse_mode="HTML"
    )

    await main_menu(message=callback_query.message)


@end_point_router.callback_query(F.text == "postpone_discount")
async def postpone_discount(callback_query: CallbackQuery):
    await hide_buttons(callback_query=callback_query)

    await callback_query.message.answer("Бонус отложен. Спасибо за за игру! Возвращаю вас в главное меню. Chao!")
    await main_menu(message=callback_query.message)


# Event to end the game
@end_point_router.message(F.text == "Отмена игры")
async def finish_game(message: Message):
    # Завершите игру и вернитесь в основное меню
    await bot.send_message(
        chat_id=message.chat.id,
        text="Игра завершена. Вернемся в основное меню.",
    )
    await main_menu(message)
