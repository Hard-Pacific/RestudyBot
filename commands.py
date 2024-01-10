from aiogram import Dispatcher, types

async def set_default_commands(dp: Dispatcher) -> None:
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Давай приступим!🤠"),
            types.BotCommand("about", "Познакомимся?😊"),
            types.BotCommand("courses", "Го учиться с нами!👨‍💻"),
            types.BotCommand("pay", "Оплата обучения за месяц🍝"),
        ]
    )
