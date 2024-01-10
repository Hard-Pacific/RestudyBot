from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from TOKEN import TOKEN

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())