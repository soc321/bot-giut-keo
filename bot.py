from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from config import TOKEN, ADMIN_IDS, INVESTMENTS
from keyboards import main_keyboard, admin_panel_kb
from utils import *
from states import InvestmentStates, WithdrawStates, DepositStates

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    is_admin = str(message.from_user.id) in ADMIN_IDS
    get_or_create_user(message.from_user.id)
    await message.answer("🎉 Chào mừng đến bot đầu tư!", reply_markup=main_keyboard(is_admin))

@dp.message_handler(Text("💼 Đầu Tư"))
async def invest_menu(message: types.Message):
    text = "📦 Các gói đầu tư:\n"
    for i, g in enumerate(INVESTMENTS, 1):
        name = g.get("name", f"Gói {g['amount']:,}đ")
        text += f"{i}. {name}: {g['amount']:,}đ, lãi {g['daily']:,}đ/ngày trong {g['days']} ngày\n"
    text += "\n➡️ Nhập số thứ tự gói muốn đầu tư:"
    await InvestmentStates.waiting_for_package_choice.set()
    await message.answer(text)

@dp.message_handler(state=InvestmentStates.waiting_for_package_choice)
async def process_invest_choice(message: types.Message, state: FSMContext):
    try:
        choice = int(message.text)
        if 1 <= choice <= len(INVESTMENTS):
            g = INVESTMENTS[choice - 1]
            user = get_or_create_user(message.from_user.id)
            if user["balance"] >= g["amount"]:
                invest(message.from_user.id, g["amount"])
                user["balance"] -= g["amount"]
                save_users(load_users())
                await message.answer(f"✅ Đầu tư gói {g.get('name', '')} thành công!")
            else:
                await message.answer("❌ Số dư không đủ để đầu tư.")
        else:
            await message.answer("❌ Vui lòng chọn số từ 1 đến 4.")
    except:
        await message.answer("❌ Vui lòng nhập số thứ tự hợp lệ.")
    await state.finish()

@dp.message_handler(Text("💸 Rút Lãi"))
async def withdraw_request(message: types.Message):
    user = get_or_create_user(message.from_user.id)
    available = calculate_profit(message.from_user.id) - sum(w["amount"] for w in user["withdrawals"])
    await message.answer(f"💰 Lãi có thể rút: {available:,}đ\n➡️ Nhập số tiền muốn rút:")
    await WithdrawStates.waiting_for_amount.set()

@dp.message_handler(state=WithdrawStates.waiting_for_amount)
async def confirm_withdraw(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        if withdraw(message.from_user.id, amount):
            await message.answer(f"✅ Yêu cầu rút {amount:,}đ đã được ghi nhận.")
        else:
            await message.answer("❌ Không đủ lãi hoặc vượt giới hạn min/max.")
    except:
        await message.answer("❌ Vui lòng nhập số tiền hợp lệ.")
    await state.finish()

@dp.message_handler(Text("💳 Nạp Tiền"))
async def deposit_start(message: types.Message):
    await message.answer("💳 Nhập số tiền bạn muốn nạp (tối thiểu 1000đ):")
    await DepositStates.waiting_for_amount.set()

@dp.message_handler(state=DepositStates.waiting_for_amount)
async def deposit_input(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount >= 1000:
            user = get_or_create_user(message.from_user.id)
            user["deposits"].append({"amount": amount, "time": current_time()})
            save_users(load_users())
            await message.answer(f"✅ Yêu cầu nạp {amount:,}đ đã được ghi nhận. Admin sẽ duyệt và cộng điểm.")
        else:
            await message.answer("❌ Vui lòng nhập số tiền hợp lệ (> 1000).")
    except:
        await message.answer("❌ Vui lòng nhập số tiền hợp lệ.")
    await state.finish()

@dp.message_handler(Text("👤 Tài Khoản"))
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

@dp.message_handler(Text("⚙️ Admin Panel"))
async def admin_panel(message: types.Message):
    if str(message.from_user.id) in ADMIN_IDS:
        await message.answer("🛠 Admin Panel:", reply_markup=admin_panel_kb)

@dp.message_handler(Text("📥 Danh Sách Nạp"))
async def view_deposits(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    data = load_users()
    text = "📥 Danh sách nạp:\n"
    for uid, u in data.items():
        for d in u.get("deposits", []):
            text += f"👤 {uid}: +{d['amount']:,}đ lúc {d['time']}\n"
    await message.answer(text or "Chưa có nạp.")

@dp.message_handler(Text("📤 Danh Sách Rút"))
async def view_withdrawals(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return
    data = load_users()
    text = "📤 Danh sách rút:\n"
    for uid, u in data.items():
        for w in u.get("withdrawals", []):
            text += f"👤 {uid}: -{w['amount']:,}đ lúc {w['time']}\n"
    await message.answer(text or "Chưa có rút.")

@dp.message_handler(Text("🔙 Quay Lại"))
async def back(message: types.Message):
    is_admin = str(message.from_user.id) in ADMIN_IDS
    await message.answer("⬅️ Quay lại menu chính", reply_markup=main_keyboard(is_admin))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
