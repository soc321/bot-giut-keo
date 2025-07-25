from aiogram import types, Dispatcher
from utils import load_users, save_users
from config import ADMIN_IDS

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, text="⚙️ Admin Cài Đặt")
    dp.register_message_handler(set_balance, commands=["add"])
    dp.register_message_handler(set_bank, commands=["bank"])

async def admin_panel(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return await message.answer("❌ Bạn không có quyền.")
    await message.answer(
        "🔧 <b>Menu Quản Trị</b>\n"
        "/add <user_id> <số điểm> — cộng điểm cho user\n"
        "/bank <user_id> <stk> — đặt STK rút cho user"
    )

async def set_balance(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    try:
        _, uid, amount = message.text.split()
        uid = str(uid)
        amount = int(amount)
        users = load_users()
        if uid not in users:
            users[uid] = {"balance": 0, "grab_count": 5, "bank": "", "recharged_this_week": 0}
        users[uid]["balance"] += amount
        save_users(users)
        await message.reply(f"✅ Đã cộng {amount:,} điểm cho {uid}")
    except:
        await message.reply("❌ Sai cú pháp. Dùng:\n/add <user_id> <số điểm>")

async def set_bank(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    try:
        _, uid, *stk = message.text.split()
        stk = " ".join(stk)
        users = load_users()
        if uid not in users:
            users[uid] = {"balance": 0, "grab_count": 5, "bank": "", "recharged_this_week": 0}
        users[uid]["bank"] = stk
        save_users(users)
        await message.reply(f"✅ Đã đặt STK cho {uid}: {stk}")
    except:
        await message.reply("❌ Sai cú pháp. Dùng:\n/bank <user_id> <stk>")
