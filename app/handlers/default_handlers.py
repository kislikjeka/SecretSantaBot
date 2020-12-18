from aiogram import types
from misc import dp


@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(message.text)