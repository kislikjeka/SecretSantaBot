import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage
from config.config import TOKEN, redis_pass
import aioredis

print(TOKEN)
storage = RedisStorage("172.28.1.4", 6379, dp=None, password=redis_pass)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)