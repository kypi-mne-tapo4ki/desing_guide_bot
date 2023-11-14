from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config.bot import bot
from config.secrets_reader import config

from models.users import get_users

admin_handlers_router: Router = Router()

admin_id = int(config.admin_id.get_secret_value())


@admin_handlers_router.message(Command("hold"))
async def get_deferred_requests(message: Message):
    user_id = message.from_user.id
    if user_id != admin_id:
        return

    users_data = await get_users(fields={"defer_discount": True})
    if not users_data:
        await bot.send_message(admin_id, text="Нет записей", parse_mode="HTML")
        return

    for user in users_data:
        send_text = "\n".join([f"<b>{key}</b>: {value}" for key, value in user.to_dict().items()])
        await bot.send_message(admin_id, text=send_text, parse_mode="HTML")


@admin_handlers_router.message(Command("users"))
async def get_last_ten_user(message: Message):
    user_id = message.from_user.id
    if user_id != admin_id:
        return

    users_data = await get_users(limit=10)
    if not users_data:
        await bot.send_message(admin_id, text="Нет записей", parse_mode="HTML")
        return

    for user in users_data:
        send_text = "\n".join([f"{key}: {value}" for key, value in user.to_dict().items()])
        await bot.send_message(admin_id, text=send_text, parse_mode="HTML")


@admin_handlers_router.message(Command("remind"))
async def remind_to_users(message: Message):
    user_id = message.from_user.id
    if user_id != admin_id:
        return

    users_data = await get_users(fields={"defer_discount": True})
    if not users_data:
        await bot.send_message(admin_id, text="Нет пользователей для напоминания.", parse_mode="HTML")
        return

    for user in users_data:
        send_text = (f"Напоминаю тебе о скидке <b>{user.discount}%</b> на услуги графического дизайнера. "
                     f"Напиши мне @theermolaeva, чтобы воспользоваться.")
        await bot.send_message(
            chat_id=user.user_id,
            text=send_text,
            parse_mode="HTML"
        )
