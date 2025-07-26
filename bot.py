import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from config import ADMIN_IDS, MIN_INVEST
from states import InvestStates, DepositStates
from utils import load_users, save_users, get_or_create_user, calculate_profit, create_deposit
from keyboards import main_menu
import time

API_TOKEN = "8121092898:AAG2FjMFjP1rjBWkaSSl_PpiMGee0StjuGg"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    get_or_create_user(message.from_user.id)
    await message.answer("🎉 Chào mừng đến với bot đầu tư!", reply_markup=main_menu)

@dp.message_handler(Text(equals="📦 Đầu Tư"))
async def invest_start(message: types.Message):
    await message.answer("💵 Nhập số tiền muốn đầu tư:")
    await InvestStates.amount.set()

@dp.message_handler(state=InvestStates.amount)
async def invest_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.replace(",", ""))
        if amount < MIN_INVEST:
            return await message.answer("❌ Vui lòng nhập số hợp lệ (> 1000đ).")
        code = f"NAP_{message.from_user.id}_{int(time.time())}"
        create_deposit(message.from_user.id, amount, code)
        await message.answer(
            f"✅ Yêu cầu nạp {amount:,}đ.\n📌 Vui lòng chuyển khoản và ghi nội dung:\n📄 {code}"
        )
        await state.finish()
    except:
        await message.answer("❌ Vui lòng nhập số hợp lệ (> 1000đ).")

@dp.message_handler(Text(equals="📨 Duyệt Nạp"))
async def approve_menu(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return await message.answer("❌ Bạn không có quyền.")
    data = load_users()
    found = False
    for uid, user in data.items():
        for d in user["deposits"]:
            if d["status"] == "pending":
                found = True
                await message.answer(
                    f"🆔 User: {uid}\n💰 Số tiền: {d['amount']:,}đ\n⏰ Thời gian: {time.strftime('%H:%M:%S %d/%m', time.localtime(d['timestamp']))}\n"
                    f"✅ Duyệt bằng: /duyet_{uid}_{d['code']}"
                )
    if not found:
        await message.answer("📭 Không có yêu cầu nạp nào.")

@dp.message_handler(lambda msg: msg.text.startswith("/duyet_"))
async def approve_deposit(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    try:
        _, uid, code = message.text.split("_", 2)
        data = load_users()
        user = data[uid]
        for d in user["deposits"]:
            if d["code"] == code and d["status"] == "pending":
                d["status"] = "approved"
                user["balance"] += d["amount"]
                save_users(data)
                return await message.answer("✅ Đã duyệt và cộng tiền.")
        await message.answer("❌ Sai cú pháp hoặc lỗi dữ liệu.")
    except:
        await message.answer("❌ Sai cú pháp hoặc lỗi dữ liệu.")

@dp.message_handler(Text(equals="📊 Thống Kê"))
async def stats(message: types.Message):
    user = get_or_create_user(message.from_user.id)
    profit = calculate_profit(message.from_user.id)
    await message.answer(
        f"🧾 Số dư: {user['balance']:,}đ\n💹 Lãi tạm tính: {profit:,}đ"
    )
