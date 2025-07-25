from aiogram import types, Dispatcher
from utils import load_users, save_users

def register_account_handlers(dp: Dispatcher):
    dp.register_message_handler(account_info, text="👤 Tài Khoản")
    dp.register_message_handler(request_recharge, commands=["nap"])
    dp.register_message_handler(request_withdraw, commands=["rut"])

async def account_info(message: types.Message):
    users = load_users()
    uid = str(message.from_user.id)

    if uid not in users:
        users[uid] = {"balance": 0, "grab_count": 5, "bank": "", "recharged_this_week": 0}
        save_users(users)

    u = users[uid]
    await message.answer(
        f"👤 <b>Tài khoản của bạn</b>:\n"
        f"💰 Số dư: {u['balance']:,} điểm\n"
        f"🎯 Lượt giật còn: {u['grab_count']}\n"
        f"🏦 STK Rút: {u['bank'] or 'Chưa đặt'}\n"
        f"🔄 Đã nạp tuần: {u['recharged_this_week']:,} điểm"
    )
