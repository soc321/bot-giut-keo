import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_IDS
from states import DepositState, WithdrawState, BankInfoState
from utils import *
from keyboards import main_menu, admin_menu

dp = Dispatcher(storage=MemoryStorage())
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

# Command /start
@dp.message(F.text == "/start")
async def start(msg: Message):
    get_user(msg.from_user.id)
    if msg.from_user.id in ADMIN_IDS:
        await msg.answer("👑 Admin Panel:", reply_markup=admin_menu)
    else:
        await msg.answer("🎉 Chào mừng bạn đến với bot đầu tư!", reply_markup=main_menu)

# 💰 Nạp tiền
@dp.message(F.text == "💰 Nạp tiền")
async def nap_tien(msg: Message, state: FSMContext):
    await msg.answer("💵 Nhập số tiền bạn muốn nạp:")
    await state.set_state(DepositState.amount)

@dp.message(DepositState.amount)
async def xuly_nap(msg: Message, state: FSMContext):
    try:
        amount = int(msg.text)
        if amount < 1000:
            return await msg.answer("❌ Vui lòng nhập số > 1000đ")
        await msg.answer(f"💳 Gửi {amount}đ tới STK: 123456789 - MB Bank\nSau đó nhắn admin để duyệt.")
        await state.clear()
    except:
        await msg.answer("❌ Vui lòng nhập số hợp lệ")

# 📤 Rút tiền
@dp.message(F.text == "📤 Rút tiền")
async def rut_tien(msg: Message, state: FSMContext):
    await msg.answer("💵 Nhập số tiền muốn rút:")
    await state.set_state(WithdrawState.amount)

@dp.message(WithdrawState.amount)
async def xuly_rut(msg: Message, state: FSMContext):
    try:
        amount = int(msg.text)
        u = get_user(msg.from_user.id)
        if amount < 1000 or amount > u["balance"]:
            return await msg.answer("❌ Số tiền không hợp lệ hoặc không đủ.")
        decrease_balance(msg.from_user.id, amount)
        await msg.answer("✅ Rút thành công. Chờ admin xử lý.")
        await state.clear()
    except:
        await msg.answer("❌ Nhập số không hợp lệ.")

# 📄 Tài khoản
@dp.message(F.text == "📄 Tài khoản")
async def taikhoan(msg: Message):
    u = get_user(msg.from_user.id)
    text = (
        f"👤 ID: <code>{msg.from_user.id}</code>\n"
        f"💰 Số dư: {u['balance']}đ\n"
        f"💼 Đầu tư: {u['invested']}đ\n"
        f"🏦 STK: {u['account']} - {u['bank']}\n"
        f"👑 Chủ TK: {u['name']}"
    )
    await msg.answer(text)

# ADMIN
@dp.message(F.text == "📥 Duyệt nạp")
async def duyet_nap(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return await msg.answer("Bạn không có quyền.")
    await msg.answer("🔧 Gửi ID và số tiền muốn cộng (vd: 123456 100000)")

@dp.message(F.text.startswith("🏠"))
async def ve_menu(msg: Message):
    if msg.from_user.id in ADMIN_IDS:
        await msg.answer("Về menu chính:", reply_markup=admin_menu)
    else:
        await msg.answer("Về menu chính:", reply_markup=main_menu)

@dp.message(F.text.regexp(r"^\d+ \d+$"))
async def admin_cong_tien(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    uid, amount = msg.text.split()
    increase_balance(int(uid), int(amount))
    await msg.answer(f"✅ Đã cộng {amount}đ cho {uid}")

# Auto cộng lãi mỗi ngày
async def auto_lai():
    while True:
        auto_add_interest()
        await asyncio.sleep(86400)  # 24 giờ

async def main():
    asyncio.create_task(auto_lai())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
