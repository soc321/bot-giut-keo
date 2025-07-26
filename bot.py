from aiogram import Bot, Dispatcher, types, executor
from config import TOKEN, ADMIN_IDS
from keyboards import main_keyboard, admin_panel_kb
from utils import *

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    is_admin = str(message.from_user.id) in ADMIN_IDS
    get_or_create_user(message.from_user.id)
    await message.answer("Chào mừng đến bot đầu tư!", reply_markup=main_keyboard(is_admin))

@dp.message_handler(text="💼 Đầu Tư")
async def invest_menu(message: types.Message):
    text = "💼 Các gói đầu tư:\n"
    for g in INVESTMENTS:
        name = g.get("name", f"Gói {g['amount']:,}đ")
        text += f"- {name}: {g['amount']:,}đ, lãi {g['daily']:,}đ/ngày trong {g['days']} ngày\n"
    text += "\nNhập số tiền bạn muốn đầu tư:"
    await message.answer(text)

@dp.message_handler(lambda m: m.text.isdigit())
async def handle_invest(message: types.Message):
    amount = int(message.text)
    user = get_or_create_user(message.from_user.id)
    if user["balance"] >= amount and invest(message.from_user.id, amount):
        user["balance"] -= amount
        save_users(load_users())
        await message.answer(f"✅ Đầu tư thành công {amount:,}đ!")
    else:
        await message.answer("❌ Không đủ số dư hoặc gói không hợp lệ.")

@dp.message_handler(text="💸 Rút Lãi")
async def handle_withdraw(message: types.Message):
    available = calculate_profit(message.from_user.id) - sum(w["amount"] for w in get_or_create_user(message.from_user.id)["withdrawals"])
    await message.answer(f"💰 Lãi có thể rút: {available:,}đ\nNhập số tiền muốn rút:")

@dp.message_handler(lambda m: m.text.isdigit())
async def confirm_withdraw(message: types.Message):
    amount = int(message.text)
    if withdraw(message.from_user.id, amount):
        await message.answer(f"✅ Yêu cầu rút {amount:,}đ đã được gửi.")
    else:
        await message.answer("❌ Không đủ lãi hoặc vượt giới hạn min/max.")

@dp.message_handler(text="👤 Tài Khoản")
async def account_info(message: types.Message):
    user = get_or_create_user(message.from_user.id)
    profit = calculate_profit(message.from_user.id) - sum(w["amount"] for w in user["withdrawals"])
    text = (
        f"👤 ID: {message.from_user.id}\n"
        f"💰 Số dư: {user['balance']:,}đ\n"
        f"📈 Lãi khả dụng: {profit:,}đ\n"
        f"🏦 STK: {user['bank']} - {user['bank_number']}"
    )
    await message.answer(text)

@dp.message_handler(commands=["bank"])
async def set_bank(message: types.Message):
    try:
        _, bank, number = message.text.split(maxsplit=2)
        user = get_or_create_user(message.from_user.id)
        user["bank"] = bank
        user["bank_number"] = number
        save_users(load_users())
        await message.answer("✅ Đã cập nhật STK.")
    except:
        await message.answer("❌ Sai cú pháp. Dùng /bank TênNgânHàng STK")

@dp.message_handler(text="⚙️ Admin Panel")
async def admin_panel(message: types.Message):
    if str(message.from_user.id) in ADMIN_IDS:
        await message.answer("🔧 Admin Panel:", reply_markup=admin_panel_kb)

@dp.message_handler(text="📥 Danh Sách Nạp")
async def view_deposits(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    data = load_users()
    text = "📥 Danh sách nạp:\n"
    for uid, u in data.items():
        for d in u.get("deposits", []):
            text += f"👤 {uid}: +{d['amount']:,}đ lúc {d['time']}\n"
    await message.answer(text or "Chưa có nạp.")

@dp.message_handler(text="📤 Danh Sách Rút")
async def view_withdrawals(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    data = load_users()
    text = "📤 Danh sách rút:\n"
    for uid, u in data.items():
        for w in u.get("withdrawals", []):
            text += f"👤 {uid}: -{w['amount']:,}đ lúc {w['time']}\n"
    await message.answer(text or "Chưa có rút.")

@dp.message_handler(text="🔙 Quay Lại")
async def back(message: types.Message):
    is_admin = str(message.from_user.id) in ADMIN_IDS
    await message.answer("⬅️ Quay lại menu chính", reply_markup=main_keyboard(is_admin))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
