from aiogram import executor
from misc import dp, bot
from database import db
from config.config import admin_id, db_user, db_pass, host


async def on_shutdown(dp):
    # await bot.send_message(admin_id, "Я упаль(")
    await db.db.pop_bind().close()
    await bot.close()


async def on_startup(dp):
    await db.create_db(db_user=db_user, db_pass=db_pass, host=host)
    # await bot.send_message(admin_id, "Я запущен!")


if __name__ == "__main__":
    import handlers

    executor.start_polling(
        dp, on_shutdown=on_shutdown, on_startup=on_startup, skip_updates=True
    )
