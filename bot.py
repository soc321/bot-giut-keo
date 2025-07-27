import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from config import TOKEN, ADMIN_IDS, INVESTMENTS, BOT_BANK_NAME, BOT_BANK_NUMBER
from utils import *
from states import *
from keyboards import user_menu, admin_menu

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ==== START ====
@dp.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    data = load_users()
    get_or_create_user(message.from_user.id, data)
    save_users(data)
    is_admin = str(message.from_user.id) in ADMIN_IDS
    await message.answer("🎉 Chào mừng bạn đến với bot đầu tư!", reply_markup=admin_menu() if is_admin else user_menu())

# ==== ĐẦU TƯ ====
@dp.message(F.text == "💼 Đầu tư")
async def show_packages(message: Message, state: FSMContext):
    await state.set_state(InvestmentStates.choosing_package)
    text = "<b>📦 Các gói đầu tư:</b>\n"
    for i, p in enumerate(INVESTMENTS, 1):
        text += f"{i}. {p['name']}: {p['amount']:,}đ - Nhận {p['daily']:,}đ/ngày trong {p['days']} ngày\n"
    text += "\nNhập số thứ tự gói bạn muốn đầu tư:"
    await message.answer(text)

@dp.message(InvestmentStates.choosing_package)
async def process_invest(message: Message, state: FSMContext):
    try:
        choice = int(message.text.strip()) - 1
        package = INVESTMENTS[choice]
    except:
        await state.clear()
        return await message.answer("❌ Vui lòng nhập số hợp lệ.")

    data = load_users()
    user = get_or_create_user(message.from_user.id, data)
    if user["balance"] < package["amount"]:
        await state.clear()
        return await message.answer("❌ Bạn không đủ số dư.")
    
    invest(message.from_user.id, package)
    await message.answer(f"✅ Đầu tư gói <b>{package['name']}</b> thành công.")
    await state.clear()

# ==== NẠP TIỀN ====
@dp.message(F.text == "💳 Nạp tiền")
async def ask_deposit(message: Message, state: FSMContext):
    await state.set_state(DepositStates.entering_amount)
    await message.answer("💳 Nhập số tiền muốn nạp:")

@dp.message(DepositStates.entering_amount)
async def save_deposit(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
        if amount < 1000:
            raise ValueError
    except:
        return await message.answer("❌ Nhập số hợp lệ (>1000).")
    data = load_users()
    user = get_or_create_user(message.from_user.id, data)
    user["deposits"].append({"amount": amount, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    save_users(data)
    await state.clear()
    await message.answer(
        f"✅ Ghi nhận nạp {amount:,}đ\n"
        f"👉 Chuyển tới: {BOT_BANK_NAME} - {BOT_BANK_NUMBER}\n"
        f"Nội dung: NAP {message.from_user.id}"
    )

# ==== RÚT TIỀN ====
@dp.message(F.text == "💸 Rút lãi")
async def ask_withdraw(message: Message, state: FSMContext):
    await state.set_state(WithdrawStates.entering_amount)
    profit = calculate_profit(message.from_user.id)
    data = load_users()
    user = get_or_create_user(message.from_user.id, data)
    withdrawn = sum(w["amount"] for w in user["withdrawals"])
    available = profit - withdrawn
    await message.answer(f"💰 Lãi khả dụng: {available:,}đ\n👉 Nhập số tiền muốn rút:")

@dp.message(WithdrawStates.entering_amount)
async def process_withdraw(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
    except:
        return await message.answer("❌ Nhập số hợp lệ.")

    if withdraw(message.from_user.id, amount):
        await message.answer("✅ Gửi yêu cầu rút thành công. Admin sẽ xử lý.")
    else:
        await message.answer("❌ Số tiền không hợp lệ.")
    await state.clear()

# ==== TÀI KHOẢN ====
@dp.message(F.text == "📄 Tài khoản")
async def account_info(message: Message):
    user = get_or_create_user(message.from_user.id)
    profit = calculate_profit(message.from_user.id)
    withdrawn = sum(w["amount"] for w in user["withdrawals"])
    available = profit - withdrawn
    await message.answer(
        f"👤 ID: {message.from_user.id}\n"
        f"💰 Số dư: {user['balance']:,}đ\n"
        f"📈 Lãi khả dụng: {available:,}đ\n"
        f"🏦 STK: {user['bank']} - {user['bank_number']}"
    )

# ==== ADMIN ====
@dp.message(F.text == "⚙️ Admin Panel")
async def admin_panel(message: Message):
    if str(message.from_user.id) in ADMIN_IDS:
        await message.answer("🔧 Admin Panel:", reply_markup=admin_menu())

@dp.message(F.text == "📥 Duyệt nạp")
async def approve_deposit(message: Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    data = load_users()
    text = ""
    for uid, u in data.items():
        for d in u["deposits"]:
            text += f"👤 {uid}: +{d['amount']:,}đ lúc {d['time']}\n"
    await message.answer(text or "Không có giao dịch nạp.")

@dp.message(F.text == "📊 Thống kê")
async def stats(message: Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    data = load_users()
    total = len(data)
    total_bal = sum(u["balance"] for u in data.values())
    await message.answer(f"📊 Tổng người dùng: {total}\n💰 Tổng số dư: {total_bal:,}đ")

@dp.message(F.text == "🔙 Quay lại")
async def back_menu(message: Message):
    is_admin = str(message.from_user.id) in ADMIN_IDS
    await message.answer("⬅️ Quay lại menu chính", reply_markup=admin_menu() if is_admin else user_menu())

# ==== AUTO LÃI ====
async def auto_profit_task():
    while True:
        data = load_users()
        save_users(data)
        await asyncio.sleep(86400)

# ==== CHẠY BOT ====
async def main():
    asyncio.create_task(auto_profit_task())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
