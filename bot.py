import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN
from keyboards import main_menu  # ✅ đúng với file keyboards.py bạn đang dùng
from taikhoan import register_account_handlers
from candy import register_candy_handlers
from admin import register_admin_handlers
from utils import reset_grab_counts_daily, reset_recharge_weekly

# Logging
logging.basicConfig(level=logging.INFO)

# Bot setup
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# Gửi menu chính khi user nhấn /start
@dp.message_handler(commands=["start"])
async def start_handler(msg: types.Message):
    user_id = str(msg.from_user.id)
    users = load_json("users_data.json")
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "daily_grabs": 0,
            "bank": "",
            "ref": None,
            "recharged": 0,
            "can_grab": False,
            "join_date": str(datetime.now())
        }
        # Ghi nhận người giới thiệu
        args = msg.get_args()
        if args and args != user_id:
            users[user_id]["ref"] = args
    save_json("users_data.json", users)
    await msg.answer("👋 Chào mừng bạn đến với bot Giựt Hũ Kẹo!", reply_markup=main_keyboard(msg.from_user.id))

# Gửi menu khi bấm nút "🏠 Menu"
@dp.message_handler(lambda m: m.text == "🏠 Menu")
async def menu(msg: types.Message):
    await msg.reply("🏠 Menu chính:", reply_markup=main_keyboard(msg.from_user.id))

# Đăng ký các handler con
register_account_handlers(dp)
register_candy_handlers(dp)
register_admin_handlers(dp)

# Reset lượt giựt mỗi ngày
reset_grab_counts_daily()
# Reset trạng thái nạp lại mỗi tuần
reset_recharge_weekly()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
