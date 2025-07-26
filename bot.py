import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart, Text, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN, ADMIN_IDS, INVESTMENTS, BOT_BANK_NAME, BOT_BANK_NUMBER
from keyboards import main_keyboard, admin_panel_kb
from states import InvestmentStates, WithdrawStates, DepositStates
from utils import *

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ========== START ==========
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    is_admin = str(message.from_user.id) in ADMIN_IDS
    get_or_create_user(message.from_user.id)
    await message.answer("🎉 Chào mừng đến với bot đầu tư!", reply_markup=main_keyboard(is_admin))

# ========== ĐẦU TƯ ==========
@dp.message(Text("💼 Đầu Tư"))
async def show_investment(message: Message, state: FSMContext):
    await state.clear()
    text = "📦 Các gói đầu tư:\n"
    for i, g in enumerate(INVESTMENTS, 1):
        text += f"{i}. {g['name']}: {g['amount']:,}đ - {g['daily']:,}đ/ngày trong {g['days']} ngày\n"
    text += "\n👉 Nhập số thứ tự gói muốn đầu tư:"
    await message.answer(text)
    await state.set_state(InvestmentStates.waiting_for_package_choice)

@dp.message(InvestmentStates.waiting_for_package_choice)
async def process_package(message: Message, state: FSMContext):
    try:
        idx = int(message.text.strip()) - 1
        if idx < 0 or idx >= len(INVESTMENTS):
            raise ValueError
    except:
        await message.answer("❌ Vui lòng nhập số thứ tự hợp lệ.")
        return
    data = load_users()
    user = get_or_create_user(message.from_user.id, data)
    package = INVESTMENTS[idx]
    if user["balance"] < package["amount"]:
        await message.answer("❌ Bạn không đủ số dư để đầu tư gói này.")
    else:
        user["balance"] -= package["amount"]
        save_users(data)
        invest(message.from_user.id, package)
        await message.answer(f"✅ Bạn đã đầu tư vào {package['name']}!")
    await state.clear()

# ========== RÚT LÃI ==========
@dp.message(Text("💸 Rút Lãi"))
async def ask_withdraw(message: Message, state: FSMContext):
    await state.clear()
    user = get_or_create_user(message.from_user.id)
    profit = calculate_profit(message.from_user.id)
    withdrawn = sum(w["amount"] for w in user["withdrawals"])
    available = profit - withdrawn
    await message.answer(f"💰 Lãi khả dụng: {available:,}đ\n👉 Nhập số tiền muốn rút:")
    await state.set_state(WithdrawStates.waiting_for_amount)

@dp.message(WithdrawStates.waiting_for_amount)
async def process_withdraw(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
    except:
        await message.answer("❌ Nhập số tiền hợp lệ.")
        return
    if withdraw(message.from_user.id, amount):
        await message.answer(f"✅ Yêu cầu rút {amount:,}đ đã được ghi nhận. Admin sẽ duyệt.")
    else:
        await message.answer("❌ Số tiền không hợp lệ hoặc vượt quá lãi khả dụng.")
    await state.clear()

# ========== NẠP TIỀN ==========
@dp.message(Text("💳 Nạp Tiền"))
async def ask_deposit(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("💳 Nhập số tiền bạn muốn nạp:")
    await state.set_state(DepositStates.waiting_for_amount)

@dp.message(DepositStates.waiting_for_amount)
async def confirm_deposit(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
        if amount < 1000:
            raise ValueError
    except:
        await message.answer("❌ Vui lòng nhập số hợp lệ (> 1000đ).")
        return

    data = load_users()
    user = get_or_create_user(message.from_user.id, data)
    user["deposits"].append({
        "amount": amount,
        "time": current_time()
    })
    save_users(data)
    await message.answer(
        f"✅ Đã ghi nhận yêu cầu nạp {amount:,}đ\n\n"
        f"💳 Chuyển khoản tới:\n🏦 {BOT_BANK_NAME} - {BOT_BANK_NUMBER}\n"
        f"📄 Nội dung: NAP {message.from_user.id}"
    )
    await state.clear()

# ========== TÀI KHOẢN ==========
@dp.message(Text("👤 Tài Khoản"))
async def account(message: Message, state: FSMContext):
    await state.clear()
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

# ========== ADMIN ==========
@dp.message(Text("⚙️ Admin Panel"))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    if str(message.from_user.id) in ADMIN_IDS:
        await message.answer("🔧 Admin Panel:", reply_markup=admin_panel_kb)

@dp.message(Text("📥 Duyệt Nạp"))
async def view_deposits(message: Message, state: FSMContext):
    await state.clear()
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    data = load_users()
    text = "📥 Danh sách nạp:\n"
    for uid, u in data.items():
        for d in u["deposits"]:
            text += f"👤 {uid}: {d['amount']:,}đ lúc {d['time']}\n"
    await message.answer(text or "✅ Không có yêu cầu nạp nào.")

@dp.message(Text("📊 Thống Kê"))
async def stats(message: Message, state: FSMContext):
    await state.clear()
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    data = load_users()
    total_users = len(data)
    total_balance = sum(u["balance"] for u in data.values())
    total_profit = sum(calculate_profit(uid) for uid in data)
    await message.answer(
        f"📊 Tổng người dùng: {total_users}\n"
        f"💰 Tổng số dư: {total_balance:,}đ\n"
        f"📈 Tổng lãi toàn hệ thống: {total_profit:,}đ"
    )

@dp.message(Text("🔙 Quay Lại"))
async def back(message: Message, state: FSMContext):
    await state.clear()
    is_admin = str(message.from_user.id) in ADMIN_IDS
    await message.answer("⬅️ Quay lại menu chính", reply_markup=main_keyboard(is_admin))

# ========== CHẠY BOT ==========
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    import asyncio
    from aiogram import executor
    asyncio.run(dp.start_polling(bot))
