import logging
import time
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from config import API_TOKEN, ADMIN_IDS
from states import DepositStates, WithdrawStates, InvestmentStates
from utils import load_users, save_users, get_or_create_user, calculate_profit

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

# ====== Keyboard ======
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("📦 Đầu Tư"), KeyboardButton("💸 Rút Lãi"))
main_menu.add(KeyboardButton("💳 Nạp Tiền"), KeyboardButton("👤 Tài Khoản"))
main_menu.add(KeyboardButton("🛠 Admin Panel")) if str(ADMIN_IDS[0]) else None

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.add(KeyboardButton("📥 Duyệt Nạp"), KeyboardButton("📊 Thống Kê"))
admin_menu.add(KeyboardButton("🔙 Quay Lại"))

# ====== Start ======
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("🎉 Chào mừng đến với bot đầu tư!", reply_markup=main_menu)

# ====== Tài Khoản ======
@dp.message_handler(Text("👤 Tài Khoản"))
async def account_info(message: types.Message, state: FSMContext):
    await state.finish()
    data = load_users()
    user = get_or_create_user(data, message.from_user.id)

    profit = calculate_profit(message.from_user.id)
    withdrawn = sum(w["amount"] for w in user["withdrawals"])
    available = profit - withdrawn

    text = (
        f"👤 ID: {message.from_user.id}\n"
        f"💰 Số dư: {user['balance']:,}đ\n"
        f"📈 Lãi tích lũy: {profit:,}đ\n"
        f"💸 Đã rút: {withdrawn:,}đ\n"
        f"✅ Có thể rút: {available:,}đ"
    )
    await message.answer(text)

# ====== Nạp Tiền ======
@dp.message_handler(Text("💳 Nạp Tiền"))
async def deposit_start(message: types.Message):
    await message.answer("💳 Nhập số tiền bạn muốn nạp:")
    await DepositStates.waiting_for_amount.set()

@dp.message_handler(state=DepositStates.waiting_for_amount)
async def deposit_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount < 1000:
            raise ValueError
    except:
        return await message.answer("❌ Vui lòng nhập số hợp lệ (> 1000đ).")

    data = load_users()
    user = get_or_create_user(data, message.from_user.id)
    deposit_code = str(random.randint(100000000, 999999999))

    user["deposits"].append({
        "amount": amount,
        "timestamp": int(time.time()),
        "status": "pending",
        "code": deposit_code
    })

    save_users(data)

    await message.answer(
        f"✅ Yêu cầu nạp {amount:,}đ đã được ghi nhận.\n\n"
        f"📌 Vui lòng chuyển khoản tới:\n"
        f"🏦 MB Bank - 1234567890\n"
        f"📄 Nội dung: NAP {deposit_code}"
    )
    await state.finish()

# ====== Admin: Duyệt Nạp ======
@dp.message_handler(Text("🛠 Admin Panel"))
async def admin_panel(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return await message.answer("⛔ Bạn không có quyền truy cập.")
    await message.answer("🛠 Admin Panel:", reply_markup=admin_menu)

@dp.message_handler(Text("📥 Duyệt Nạp"))
async def approve_deposits(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    data = load_users()
    pending = []
    for user_id, user in data.items():
        for d in user["deposits"]:
            if d["status"] == "pending":
                pending.append((user_id, d))

    if not pending:
        return await message.answer("📪 Không có yêu cầu nạp nào.")

    for uid, d in pending:
        bot_msg = (
            f"🆔 User: {uid}\n"
            f"💵 Số tiền: {d['amount']:,}đ\n"
            f"⏰ Thời gian: {time.strftime('%H:%M:%d/%m', time.localtime(d['timestamp']))}\n"
            f"✅ Duyệt bằng: /duyet_{uid}_{d['code']}"
        )
        await message.answer(bot_msg)

@dp.message_handler(lambda m: m.text.startswith("/duyet_"))
async def confirm_deposit(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return

    try:
        _, uid, code = message.text.split("_")
        data = load_users()
        user = data.get(uid)
        if not user:
            raise ValueError

        for d in user["deposits"]:
            if d["code"] == code and d["status"] == "pending":
                user["balance"] += d["amount"]
                d["status"] = "approved"
                save_users(data)
                return await message.answer(f"✅ Đã cộng {d['amount']:,}đ cho user {uid}.")

        await message.answer("❌ Không tìm thấy giao dịch.")
    except:
        await message.answer("❌ Sai cú pháp hoặc lỗi dữ liệu.")

# ====== Rút Lãi ======
@dp.message_handler(Text("💸 Rút Lãi"))
async def withdraw_start(message: types.Message):
    await message.answer("💸 Nhập số tiền bạn muốn rút:")
    await WithdrawStates.waiting_for_amount.set()

@dp.message_handler(state=WithdrawStates.waiting_for_amount)
async def withdraw_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount < 7000 or amount > 500000:
            return await message.answer("❌ Số tiền không hợp lệ (7k - 500k).")
    except:
        return await message.answer("❌ Vui lòng nhập số hợp lệ.")

    data = load_users()
    user = get_or_create_user(data, message.from_user.id)

    profit = calculate_profit(message.from_user.id)
    withdrawn = sum(w["amount"] for w in user["withdrawals"])
    available = profit - withdrawn

    if amount > available:
        return await message.answer("❌ Số tiền không hợp lệ hoặc vượt quá lãi khả dụng.")

    user["withdrawals"].append({
        "amount": amount,
        "timestamp": int(time.time())
    })
    save_users(data)

    await message.answer(f"✅ Đã gửi yêu cầu rút {amount:,}đ. Admin sẽ xử lý sớm nhất.")
    await state.finish()

# ====== Đầu Tư ======
@dp.message_handler(Text("📦 Đầu Tư"))
async def choose_package(message: types.Message):
    await message.answer(
        "📦 Các gói đầu tư:\n"
        "1. Gói Trải Nghiệm: 5,000đ - 2,000đ/ngày trong 7 ngày\n"
        "2. Gói Tiết Kiệm: 20,000đ - 5,000đ/ngày trong 7 ngày\n"
        "3. Gói Lợi Nhuận: 50,000đ - 5,000đ/ngày trong 15 ngày\n"
        "4. Gói Siêu Lãi: 100,000đ - 5,000đ/ngày trong 30 ngày\n\n"
        "👉 Nhập số thứ tự gói bạn muốn đầu tư:"
    )
    await InvestmentStates.waiting_for_package_choice.set()

@dp.message_handler(state=InvestmentStates.waiting_for_package_choice)
async def handle_package_choice(message: types.Message, state: FSMContext):
    packages = {
        "1": {"amount": 5000, "daily_profit": 2000, "duration": 7},
        "2": {"amount": 20000, "daily_profit": 5000, "duration": 7},
        "3": {"amount": 50000, "daily_profit": 5000, "duration": 15},
        "4": {"amount": 100000, "daily_profit": 5000, "duration": 30},
    }

    choice = message.text.strip()
    if choice not in packages:
        return await message.answer("❌ Vui lòng nhập số thứ tự hợp lệ.")

    data = load_users()
    user = get_or_create_user(data, message.from_user.id)

    package = packages[choice]
    if user["balance"] < package["amount"]:
        await message.answer("❌ Số dư không đủ để đầu tư gói này.")
        return await state.finish()

    user["balance"] -= package["amount"]
    user["investments"].append({
        "amount": package["amount"],
        "daily_profit": package["daily_profit"],
        "duration": package["duration"],
        "start_time": int(time.time())
    })

    save_users(data)

    await message.answer(
        f"✅ Bạn đã đầu tư gói {choice} thành công!\n"
        f"Số tiền: {package['amount']:,}đ\n"
        f"Lãi mỗi ngày: {package['daily_profit']:,}đ\n"
        f"Thời gian: {package['duration']} ngày"
    )
    await state.finish()

# ====== Run ======
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
