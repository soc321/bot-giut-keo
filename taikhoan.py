from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import ADMIN_ID
from utils import load_json, save_json
from config import REQUIRED_RECHARGE
from aiogram.types import ReplyKeyboardRemove

def register_account_handlers(dp: Dispatcher):
    @dp.message_handler(lambda m: m.text == "👤 Tài khoản")
    async def handle_account(msg: types.Message):
        users = load_json("users_data.json")
        user_id = str(msg.from_user.id)
        user = users.get(user_id, {
            "balance": 0,
            "daily_grabs": 0,
            "bank": "",
            "ref": None,
            "recharged": 0,
            "can_grab": False
        })
        text = f"""👤 Tài khoản của bạn:
💰 Số dư: {user.get("balance", 0)} điểm
🎯 Lượt giựt còn lại: {5 - user.get("daily_grabs", 0)} / 5
🏦 STK rút tiền: {user.get("bank", "Chưa có")}\n"""
        await msg.reply(text)

    @dp.message_handler(lambda m: m.text == "🔗 Mời bạn bè")
    async def invite(msg: types.Message):
        link = f"https://t.me/{msg.bot.username}?start={msg.from_user.id}"
        await msg.reply(f"🔗 Mời bạn bè bằng link:\n{link}")

    @dp.message_handler(lambda m: m.text == "💸 Rút điểm")
    async def withdraw(msg: types.Message):
        await msg.reply("💬 Vui lòng nhập thông tin rút điểm theo cú pháp:\n\n/momo hoặc Tên ngân hàng + Số tài khoản + Số tiền")

    @dp.message_handler(commands=["momo"])
    async def handle_withdraw(msg: types.Message):
        await msg.bot.send_message(ADMIN_ID, f"📤 Yêu cầu rút tiền từ {msg.from_user.id}:\n{msg.text}")
        await msg.reply("✅ Đã gửi yêu cầu rút tiền đến admin.")