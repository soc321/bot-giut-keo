import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram.enums.parse_mode import ParseMode

from config import TOKEN, ADMIN_IDS, MIN_WITHDRAW, MAX_WITHDRAW, DEPOSIT_PACKAGES
from states import DepositState, WithdrawState
from utils import *
from keyboards import main_menu, back_menu

import asyncio
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def start(msg: Message):
    get_or_create_user(msg.from_user.id)
    await msg.answer("🎉 Chào mừng đến với bot đầu tư!", reply_markup=main_menu)

@dp.message(F.text == "📦 Đầu Tư")
async def deposit(msg: Message, state: FSMContext):
    await msg.answer("💵 Nhập số tiền muốn đầu tư (≥ 1000đ):", reply_markup=back_menu)
    await state.set_state(DepositState.amount)

@dp.message(DepositState.amount)
async def process_deposit(msg: Message, state: FSMContext):
    try:
        amount = int(msg.text)
        if amount < 1000:
            raise ValueError
    except:
        return await msg.answer("❌ Vui lòng nhập số hợp lệ (≥ 1000đ).")

    data = load_users()
    user = get_or_create_user(msg.from_user.id)
    deposit_code = f"{msg.from_user.id}_{int(time.time())}"
    user["deposits"].append({
        "amount": amount,
        "timestamp": int(time.time()),
        "status": "pending",
        "code": deposit_code
    })
    save_users(data)

    await msg.answer(
        f"✅ Yêu cầu nạp {amount:,}đ\n📌 Vui lòng chuyển khoản và chờ admin duyệt.\n🧾 Nội dung: NAP {deposit_code}"
    )
    await state.clear()

@dp.message(F.text == "📥 Duyệt Nạp")
async def approve_panel(msg: Message):
    if str(msg.from_user.id) not in ADMIN_IDS:
        return await msg.answer("Bạn không có quyền.")
    
    pending = get_pending_deposits()
    if not pending:
        return await msg.answer("📭 Không có yêu cầu nạp nào.")
    
    for uid, d in pending:
        await msg.answer(
            f"<b>ID:</b> {uid}\n💰 Số tiền: {d['amount']:,}đ\n⏰ Thời gian: {time.strftime('%H:%M:%d/%m', time.localtime(d['timestamp']))}\n✅ Duyệt bằng:\n/duyet_{uid}_{d['code']}"
        )

@dp.message(Command("duyet"))
async def approve_command(msg: Message):
    try:
        _, uid, code = msg.text.split("_", 2)
        data = load_users()
        user = data.get(uid)
        if not user:
            raise Exception

        for d in user["deposits"]:
            if d["code"] == code and d["status"] == "pending":
                d["status"] = "approved"
                d["rate"] = 0.01  # Gắn rate tạm
                save_users(data)
                return await msg.answer("✅ Duyệt thành công.")
        raise Exception
    except:
        await msg.answer("❌ Sai cú pháp hoặc lỗi dữ liệu.")

@dp.message(F.text == "💸 Rút Lãi")
async def withdraw_start(msg: Message, state: FSMContext):
    await msg.answer("💸 Nhập số tiền muốn rút:", reply_markup=back_menu)
    await state.set_state(WithdrawState.amount)

@dp.message(WithdrawState.amount)
async def withdraw_process(msg: Message, state: FSMContext):
    try:
        amount = int(msg.text)
        if amount < MIN_WITHDRAW or amount > MAX_WITHDRAW:
            raise ValueError
    except:
        return await msg.answer(f"❌ Vui lòng nhập số hợp lệ (> {MIN_WITHDRAW}đ).")

    profit = calculate_profit(msg.from_user.id)
    if amount > profit:
        return await msg.answer("❌ Không đủ lãi để rút.")

    data = load_users()
    user = data[str(msg.from_user.id)]
    user["withdraws"].append({
        "amount": amount,
        "timestamp": int(time.time())
    })
    save_users(data)
    await msg.answer("✅ Yêu cầu rút đã ghi nhận. Vui lòng chờ duyệt.")
    await state.clear()

@dp.message(F.text == "📊 Thống Kê")
async def stats(msg: Message):
    user = get_or_create_user(msg.from_user.id)
    total_invest = sum(d["amount"] for d in user["deposits"] if d["status"] == "approved")
    profit = calculate_profit(msg.from_user.id)
    withdrawn = sum(w["amount"] for w in user["withdraws"])
    balance = profit - withdrawn
    await msg.answer(
        f"💰 Tổng đầu tư: {total_invest:,}đ\n📈 Lãi: {profit:,}đ\n💸 Đã rút: {withdrawn:,}đ\n💼 Có thể rút: {balance:,}đ"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
