from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import user, admin

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

user.register(dp)
admin.register(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)