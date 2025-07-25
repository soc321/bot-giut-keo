from aiogram import types
from aiogram.dispatcher import Dispatcher
from utils import load_json, save_json
from keyboards import main_menu

def register_account_handlers(dp: Dispatcher):
    @dp.message_handler(commands=["start"])
    async def start(msg: types.Message):
        users = load_json("users_data.json")
        uid = str(msg.from_user.id)
        if uid not in users:
            users[uid] = {
                "balance": 0,
                "turns": 0,
                "bank": "Chưa có",
                "recharged": 0,
                "can_grab": False
            }
            save_json("users_data.json", users)
        await msg.answer("🎉 Chào mừng đến với game Giựt Hũ Kẹo!", reply_markup=main_menu)

    @dp.message_handler(lambda msg: msg.text == "👤 Tài Khoản")
    async def show_account(msg: types.Message):
        uid = str(msg.from_user.id)
        users = load_json("users_data.json")
        user = users.get(uid)
        if not user:
            return await msg.reply("⚠️ Không tìm thấy tài khoản.")
        await msg.reply(
            f"👤 Tài khoản của bạn:\n"
            f"💰 Số dư: {user['balance']} điểm\n"
            f"🎯 Lượt giựt còn: {user['turns']}\n"
            f"🏦 STK rút: {user['bank']}"
        )

    @dp.message_handler(lambda msg: msg.text == "🔗 Mời Bạn Bè")
    async def invite_friends(msg: types.Message):
        invite_link = f"https://t.me/{(await msg.bot.get_me()).username}?start={msg.from_user.id}"
        await msg.reply(f"📨 Mời bạn bè qua link:\n{invite_link}")

    @dp.message_handler(commands=["momo"])
    async def withdraw_request(msg: types.Message):
        uid = str(msg.from_user.id)
        args = msg.text.split(maxsplit=3)
        if len(args) < 4:
            return await msg.reply("❌ Sai cú pháp. Dùng: /momo TênNH STK SốTiền")
        _, bank, stk, amount = args
        await msg.bot.send_message(
            6730559072,  # ID Admin
            f"💸 YÊU CẦU RÚT ĐIỂM\n👤 ID: {uid}\n🏦 Ngân hàng: {bank}\n🔢 STK: {stk}\n💰 Số tiền: {amount}"
        )
        await msg.reply("✅ Yêu cầu rút đã được gửi tới admin.")

    @dp.message_handler(lambda msg: msg.text.startswith("💳 Đặt STK "))
    async def set_bank(msg: types.Message):
        uid = str(msg.from_user.id)
        stk = msg.text.replace("💳 Đặt STK ", "").strip()
        users = load_json("users_data.json")
        if uid not in users:
            return await msg.reply("❌ Tài khoản không tồn tại.")
        users[uid]["bank"] = stk
        save_json("users_data.json", users)
        await msg.reply(f"✅ Đã cập nhật STK rút: {stk}")