from aiogram import types
from misc import dp, bot
from config.config import admin_id


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    if 123 == 123:
        print("Kek")
    print(message.from_user.id)
    text = (
        "Добро пожаловать в тайного санту \n"
        + "Для работы с ботом напиши команду /newgroup \n"
    )
    await message.answer(message.from_user.id)
    await message.answer(admin_id)


@dp.message_handler(commands=["newgroup"])
async def cmd_start(message: types.Message):
    text = "Добро пожаловать в тайного санту \n"
    "Для работы с ботом напиши команду /newgroup"
    ""
    await message.answer(text)


@dp.message_handler(commands="set_commands", state="*")
async def cmd_set_commands(message: types.Message):
    if message.from_user.id == int(admin_id):  # Подставьте сюда свой Telegram ID
        commands = [
            types.BotCommand(command="/newgroup", description="Создать группу"),
            types.BotCommand(command="/groups", description="Просмотреть мои группы"),
            types.BotCommand(command="/profile", description="Просмотреть мои анкеты"),
        ]
        await bot.set_my_commands(commands)
        await message.answer("Команды настроены.")