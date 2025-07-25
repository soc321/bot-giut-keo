import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import ADMIN_IDS
from keyboards import main_keyboard
from candy import register_candy_handlers
from account import register_account_handlers
from admin import register_admin_handlers
from utils import reset_grab_counts_daily, reset_recharge_weekly

API_TOKEN = "8121092898:AAG2FjMFjP1rjBWkaSSl_PpiMGee0StjuGg"

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    buttons = main_keyboard(message.from_user.id)
    await message.answer("🍬 Xin chào! Chọn chức năng:", reply_markup=buttons)

def main():
    register_candy_handlers(dp)
    register_account_handlers(dp)
    register_admin_handlers(dp)

    # Reset lượt giật mỗi ngày và reset nạp mỗi tuần nếu cần
    reset_grab_counts_daily()
    reset_recharge_weekly()

    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main()
