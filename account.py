from aiogram import types, Dispatcher
from utils import load_users, save_users


# 👤 Hiện thông tin tài khoản
async def account_info(message: types.Message):
    users = load_users()
    uid = str(message.from_user.id)

    users.setdefault(uid, {
    "balance": 0,
    "grab_count": 5,
    "bank": "",
    "recharged_this_week": 0
})
        save_users(users)

    u = users[uid]
    await message.answer(
        f"👤 <b>Tài khoản của bạn</b>:\n"
        f"💰 Số dư: {u['balance']:,} điểm\n"
        f"🎯 Lượt giật còn: {u['grab_count']}\n"
        f"🏦 STK Rút: {u['bank'] or 'Chưa đặt'}\n"
        f"🔄 Đã nạp tuần: {u['recharged_this_week']:,} điểm"
    )


# 💳 Đặt STK rút
async def set_bank_account(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("❌ Dùng đúng cú pháp: /bank số_tài_khoản")

    users = load_users()
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {"balance": 0, "grab_count": 5, "bank": "", "recharged_this_week": 0}

    users[uid]["bank"] = parts[1].strip()
    save_users(users)
    await message.answer("✅ Đã cập nhật STK rút điểm.")


# ➕ Gửi yêu cầu nạp điểm
async def request_recharge(message: types.Message):
    try:
        amount = int(message.text.split()[1])
        if amount <= 0:
            raise ValueError
    except:
        return await message.answer("❌ Dùng đúng cú pháp: /nap 10000")

    users = load_users()
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {"balance": 0, "grab_count": 5, "bank": "", "recharged_this_week": 0}

    users[uid]["recharged_this_week"] += amount
    save_users(users)

    await message.answer(
        f"🧾 Đã ghi nhận bạn nạp <b>{amount:,} điểm</b>.\n"
        "Gửi ảnh chuyển khoản cho admin để được cộng điểm."
    )


# ➖ Gửi yêu cầu rút điểm
async def request_withdraw(message: types.Message):
    try:
        amount = int(message.text.split()[1])
        if amount <= 0:
            raise ValueError
    except:
        return await message.answer("❌ Dùng đúng cú pháp: /rut 5000")

    users = load_users()
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {"balance": 0, "grab_count": 5, "bank": "", "recharged_this_week": 0}

    user = users[uid]
    if user["balance"] < amount:
        return await message.answer("❌ Bạn không đủ điểm để rút.")
    if not user["bank"]:
        return await message.answer("⚠️ Bạn chưa đặt STK. Gửi /bank <stk> để đặt.")

    user["balance"] -= amount
    save_users(users)

    await message.answer(
        f"💸 Đã gửi yêu cầu rút <b>{amount:,} điểm</b> về STK:\n"
        f"<code>{user['bank']}</code>\n"
        "Admin sẽ xử lý sớm nhất!"
    )


# 📌 Đăng ký handler
def register_account_handlers(dp: Dispatcher):
    dp.register_message_handler(account_info, text="👤 Tài Khoản")
    dp.register_message_handler(set_bank_account, commands=["bank"])
    dp.register_message_handler(request_recharge, commands=["nap"])
    dp.register_message_handler(request_withdraw, commands=["rut"])
