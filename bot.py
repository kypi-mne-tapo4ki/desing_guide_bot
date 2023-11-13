import logging

from aiogram import Bot
from config_reader import config


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())
