from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import ADMIN_ID
from utils import load_json, save_json
from keyboards import main_menu

def register_admin_handlers(dp: Dispatcher):
    @dp.message_handler(commands=["admin"])
    async def admin_panel(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return await msg.reply("❌ Bạn không có quyền truy cập.")
        await msg.reply(
            "🔧 ADMIN PANEL:\n"
            "/cong [id] [số điểm]\n"
            "/tru [id] [số điểm]\n"
            "/minmax [min] [max]\n"
            "/stats"
        )

    @dp.message_handler(commands=["cong"])
    async def add_points(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return
        try:
            _, uid, amount = msg.text.split()
            uid = str(uid)
            amount = int(amount)
        except:
            return await msg.reply("❌ Sai cú pháp. Dùng: /cong [id] [số điểm]")

        users = load_json("users_data.json")
        if uid not in users:
            return await msg.reply("❌ User không tồn tại.")
        users[uid]["balance"] += amount
        users[uid]["recharged"] += amount

        if users[uid]["recharged"] >= 5000:
            users[uid]["can_grab"] = True
        save_json("users_data.json", users)
        await msg.reply(f"✅ Đã cộng {amount} điểm cho {uid}.")

    @dp.message_handler(commands=["tru"])
    async def subtract_points(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return
        try:
            _, uid, amount = msg.text.split()
            uid = str(uid)
            amount = int(amount)
        except:
            return await msg.reply("❌ Sai cú pháp. Dùng: /tru [id] [số điểm]")

        users = load_json("users_data.json")
        if uid not in users:
            return await msg.reply("❌ User không tồn tại.")
        users[uid]["balance"] -= amount
        if users[uid]["balance"] < 0:
            users[uid]["balance"] = 0
        save_json("users_data.json", users)
        await msg.reply(f"✅ Đã trừ {amount} điểm từ {uid}.")

    @dp.message_handler(commands=["minmax"])
    async def set_min_max(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return
        try:
            _, min_val, max_val = msg.text.split()
            min_val = int(min_val)
            max_val = int(max_val)
        except:
            return await msg.reply("❌ Sai cú pháp. Dùng: /minmax [min] [max]")

        with open("config.py", "r") as f:
            lines = f.readlines()

        with open("config.py", "w") as f:
            for line in lines:
                if line.startswith("MIN_CANDY_POINT"):
                    f.write(f"MIN_CANDY_POINT = {min_val}\n")
                elif line.startswith("MAX_CANDY_POINT"):
                    f.write(f"MAX_CANDY_POINT = {max_val}\n")
                else:
                    f.write(line)

        await msg.reply(f"✅ Đã cập nhật min/max kẹo thành {min_val}/{max_val} điểm.")

    @dp.message_handler(commands=["stats"])
    async def stats(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return
        users = load_json("users_data.json")
        total_users = len(users)
        total_balance = sum(user["balance"] for user in users.values())
        total_recharged = sum(user.get("recharged", 0) for user in users.values())
        await msg.reply(
            f"👥 Tổng người dùng: {total_users}\n"
            f"💰 Tổng số dư: {total_balance} điểm\n"
            f"🔋 Tổng đã nạp: {total_recharged} điểm"
        )