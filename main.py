import asyncio
import logging

from aiogram import Bot, Dispatcher

import other_handlers
from config_reader import config
from db import init_db
from levels import end_point, first_level, second_level, start_point, third_level


async def main():
    logging.basicConfig(level=logging.INFO)

    # Bot settings
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    await asyncio.sleep(5)

    # Init db
    await init_db()

    # Handlers
    dp.include_router(start_point.start_point_router)
    dp.include_router(first_level.first_level_router)
    dp.include_router(second_level.second_level_router)
    dp.include_router(third_level.third_level_router)
    dp.include_router(end_point.end_point_router)
    dp.include_router(other_handlers.other_handlers)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
