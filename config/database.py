from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config.secrets_reader import config
from models.users import User


async def init_db():
    """init database."""
    client = AsyncIOMotorClient(config.db_host.get_secret_value())
    await init_beanie(
        database=client[config.db_name.get_secret_value()],
        document_models=[
            User,
        ],
    )
