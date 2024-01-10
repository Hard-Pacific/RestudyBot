# RESTUDY bot
# Бот для записи на занятия, оплаты курса и ответов на вопросов
from handlers import dp
from aiogram.utils import executor
from commands import set_default_commands
import database
    
async def startup(dp):
    await set_default_commands(dp)


if __name__ == "__main__":
    database.create_data()
    executor.start_polling(dp, skip_updates=True, on_startup=startup)