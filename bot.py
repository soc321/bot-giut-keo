from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from datetime import datetime
from config import TOKEN, ADMIN_IDS, INVESTMENTS, BOT_BANK_NAME, BOT_BANK_NUMBER
from keyboards import main_keyboard, admin_panel_kb
from utils import *
from states import *
import asyncio

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ========== Start ==========
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    is_admin = str(message.from_user.id) in ADMIN_IDS
    get_or_create_user(message.from_user.id)
    await message.answer("🎉 Chào mừng đến với bot đầu tư!", reply_markup=main_keyboard(is_admin))

# ========== Đầu Tư ==========
@dp.message_handler(Text("💼 Đầu Tư"))
async def invest_menu(message: types.Message):
    text = "📦 Các gói đầu tư:\n"
    for i, g in enumerate(INVESTMENTS, 1):
        text += f"{i}. {g['name']}: {g['amount']:,}đ - {g['daily']:,}đ/ngày trong {g['days']} ngày\n"
    text += "\n👉 Nhập số thứ tự gói bạn muốn đầu tư:"
    await InvestmentStates.waiting_for_package_choice.set()
    await message.answer(text)

@dp.message_handler(state=InvestmentStates.waiting_for_package_choice)
async def invest_choose(message: types.Message, state: FSMContext):
    try:
        choice = int(message.text.strip()) - 1
        if choice < 0 or choice >= len(INVESTMENTS):
            await state.finish()
            return await message.answer("❌ Vui lòng nhập số thứ tự hợp lệ.")
    except:
        await state.finish()
        return await message.answer("❌ Vui lòng nhập số thứ tự hợp lệ.")

    package = INVESTMENTS[choice]
    user = get_or_create_user(message.from_user.id)
    if user["balance"] < package["amount"]:
        await state.finish()
        return await message.answer("❌ Bạn không đủ số dư để đầu tư gói này.")

    user["balance"] -= package["amount"]
    invest(message.from_user.id, package)
    await state.finish()
    await message.answer(f"✅ Đầu tư {package['name']} thành công!")

# ========== Rút Lãi ==========
@dp.message_handler(Text("💸 Rút Lãi"))
async def ask_withdraw(message: types.Message):
    user = get_or_create_user(message.from_user.id)
    profit = calculate_profit(message.from_user.id)
    withdrawn = sum(w["amount"] for w in user["withdrawals"])
    available = profit - withdrawn
    await message.answer(f"💰 Lãi khả dụng: {available:,}đ\n👉 Nhập số tiền muốn rút:")
    await WithdrawStates.waiting_for_amount.set()

@dp.message_handler(state=WithdrawStates.waiting_for_amount)
async def process_withdraw(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
    except:
        await state.finish()
        return await message.answer("❌ Vui lòng nhập số tiền hợp lệ.")

    if withdraw(message.from_user.id, amount):
        await message.answer(f"✅ Đã gửi yêu cầu rút {amount:,}đ. Admin sẽ xử lý sớm.")
    else:
        await message.answer("❌ Số tiền không hợp lệ hoặc vượt quá lãi khả dụng.")
    await state.finish()

# ========== Nạp Tiền ==========
@dp.message_handler(Text("💳 Nạp Tiền"))
async def ask_deposit(message: types.Message):
    await message.answer("💳 Nhập số tiền bạn muốn nạp:")
    await DepositStates.waiting_for_amount.set()

@dp.message_handler(state=DepositStates.waiting_for_amount)
async def confirm_deposit(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
        if amount < 1000:
            raise ValueError
    except:
        return await message.answer("❌ Vui lòng nhập số hợp lệ (> 1000đ).")

    data = load_users()
    uid = str(message.from_user.id)
    user = get_or_create_user(uid, data)
    user["deposits"].append({
        "amount": amount,
        "time": current_time()
    })
    save_users(data)

    await message.answer(
        f"✅ Yêu cầu nạp {amount:,}đ đã được ghi nhận.\n\n"
        f"📌 Vui lòng chuyển khoản tới:\n🏦 {BOT_BANK_NAME} - {BOT_BANK_NUMBER}\n"
        f"📄 Nội dung: NAP {message.from_user.id}"
    )
    await state.finish()

# ========== Tài Khoản ==========
@dp.message_handler(Text("👤 Tài Khoản"))
async def account_info(message: types.Message):
    user = get_or_create_user(message.from_user.id)
    profit = calculate_profit(message.from_user.id)
    withdrawn = sum(w["amount"] for w in user["withdrawals"])
    available = profit - withdrawn
    text = (
        f"👤 ID: {message.from_user.id}\n"
        f"💰 Số dư: {user['balance']:,}đ\n"
        f"📈 Lãi khả dụng: {available:,}đ\n"
        f"🏦 STK: {user['bank']} - {user['bank_number']}"
    )
    await message.answer(text)

# ========== Cập nhật STK ==========
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
        await message.answer("❌ Sai cú pháp. Dùng: /bank TênNH STK")

# ========== Admin Panel ==========
@dp.message_handler(Text("⚙️ Admin Panel"))
async def admin_panel(message: types.Message):
    if str(message.from_user.id) in ADMIN_IDS:
        await message.answer("🔧 Admin Panel:", reply_markup=admin_panel_kb)

@dp.message_handler(commands=["add"])
async def admin_add(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    try:
        _, uid, amount = message.text.split()
        data = load_users()
        data[uid]["balance"] += int(amount)
        save_users(data)
        await message.answer(f"✅ Đã cộng {amount}đ cho {uid}")
    except:
        await message.answer("❌ Sai cú pháp. /add ID SốTiền")

@dp.message_handler(Text("📥 Duyệt Nạp"))
async def view_deposits(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    data = load_users()
    text = "📥 Danh sách nạp:\n"
    for uid, u in data.items():
        for d in u.get("deposits", []):
            text += f"👤 {uid}: +{d['amount']:,}đ lúc {d['time']}\n"
    await message.answer(text or "Chưa có nạp.")

@dp.message_handler(Text("📊 Thống Kê"))
async def stats(message: types.Message):
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

@dp.message_handler(Text("🔙 Quay Lại"))
async def back(message: types.Message):
    is_admin = str(message.from_user.id) in ADMIN_IDS
    await message.answer("⬅️ Quay lại menu chính", reply_markup=main_keyboard(is_admin))

# ========== Auto lãi mỗi ngày ==========
async def auto_profit_loop():
    while True:
        data = load_users()
        for uid in data:
            get_or_create_user(uid)  # bảo đảm cấu trúc
        save_users(data)
        await asyncio.sleep(86400)  # mỗi 24 giờ

# ========== Run Bot ==========
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(auto_profit_loop())
    executor.start_polling(dp, skip_updates=True)
