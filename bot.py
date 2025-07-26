from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TOKEN, ADMIN_IDS
from keyboards import main_keyboard, admin_panel_kb
from utils import *

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# --- FSM States ---
class Form(StatesGroup):
    investing = State()
    withdrawing = State()
    depositing = State()
    admin_add_point = State()

# --- /start ---
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    is_admin = str(message.from_user.id) in ADMIN_IDS
    get_or_create_user(message.from_user.id)
    await message.answer("Chào mừng đến bot đầu tư!", reply_markup=main_keyboard(is_admin))

# --- 💼 Đầu Tư ---
@dp.message_handler(text="💼 Đầu Tư")
async def invest_menu(message: types.Message):
    text = "💼 Các gói đầu tư:\n"
    for g in INVESTMENTS:
        name = g.get("name", f"Gói {g['amount']:,}đ")
        text += f"- {name}: {g['amount']:,}đ, lãi {g['daily']:,}đ/ngày trong {g['days']} ngày\n"
    text += "\nNhập số tiền bạn muốn đầu tư:"
    await Form.investing.set()
    await message.answer(text)

@dp.message_handler(state=Form.investing)
async def handle_invest(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
    except:
        return await message.answer("❌ Vui lòng nhập số tiền hợp lệ.")

    user = get_or_create_user(message.from_user.id)
    if user["balance"] >= amount and invest(message.from_user.id, amount):
        user["balance"] -= amount
        save_users(load_users())
        await message.answer(f"✅ Đầu tư thành công {amount:,}đ!")
    else:
        await message.answer("❌ Không đủ số dư hoặc số tiền không hợp lệ.")
    await state.finish()

# --- 💸 Rút Lãi ---
@dp.message_handler(text="💸 Rút Lãi")
async def handle_withdraw(message: types.Message):
    user = get_or_create_user(message.from_user.id)
    available = calculate_profit(message.from_user.id) - sum(w["amount"] for w in user["withdrawals"])
    await message.answer(f"💰 Lãi có thể rút: {available:,}đ\nNhập số tiền muốn rút:")
    await Form.withdrawing.set()

@dp.message_handler(state=Form.withdrawing)
async def confirm_withdraw(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
    except:
        return await message.answer("❌ Vui lòng nhập số tiền hợp lệ.")

    if withdraw(message.from_user.id, amount):
        await message.answer(f"✅ Yêu cầu rút {amount:,}đ đã được gửi.")
    else:
        await message.answer("❌ Không đủ lãi hoặc vượt giới hạn min/max.")
    await state.finish()

# --- 🏦 Nạp tiền ---
@dp.message_handler(commands=["nap"])
async def nap(message: types.Message):
    await message.answer("💳 Nhập số tiền bạn muốn nạp:")
    await Form.depositing.set()

@dp.message_handler(state=Form.depositing)
async def deposit_input(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError
    except:
        return await message.answer("❌ Số tiền không hợp lệ.")

    user = get_or_create_user(message.from_user.id)
    user["balance"] += amount
    user["deposits"].append({
        "amount": amount,
        "time": current_time()
    })
    save_users(load_users())
    await message.answer(f"✅ Đã nạp {amount:,}đ vào tài khoản.")
    await state.finish()

# --- 👤 Tài Khoản ---
@dp.message_handler(text="👤 Tài Khoản")
async def account_info(message: types.Message):
    user = get_or_create_user(message.from_user.id)
    profit = calculate_profit(message.from_user.id) - sum(w["amount"] for w in user["withdrawals"])
    text = (
        f"👤 ID: {message.from_user.id}\n"
        f"💰 Số dư: {user['balance']:,}đ\n"
        f"📈 Lãi khả dụng: {profit:,}đ\n"
        f"🏦 STK: {user['bank']} - {user['bank_number'] or '-'}"
    )
    await message.answer(text)

# --- /bank cập nhật STK ---
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
        await message.answer("❌ Sai cú pháp. Dùng: /bank TênNgânHàng STK")

# --- ⚙️ Admin Panel ---
@dp.message_handler(text="⚙️ Admin Panel")
async def admin_panel(message: types.Message):
    if str(message.from_user.id) in ADMIN_IDS:
        await message.answer("🔧 Admin Panel:", reply_markup=admin_panel_kb)

# --- Admin: Danh sách nạp ---
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

# --- Admin: Danh sách rút ---
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

# --- Admin: Cộng điểm ---
@dp.message_handler(commands=["cong"])
async def admin_add_balance_start(message: types.Message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return await message.answer("Bạn không có quyền.")
    await message.answer("💡 Nhập theo cú pháp: `ID sốtiền` (vd: 123456789 50000)")
    await Form.admin_add_point.set()

@dp.message_handler(state=Form.admin_add_point)
async def admin_add_balance_done(message: types.Message, state: FSMContext):
    try:
        uid, amount = message.text.split()
        uid = str(uid)
        amount = int(amount)
        data = load_users()
        if uid not in data:
            return await message.answer("❌ ID không tồn tại.")
        data[uid]["balance"] += amount
        save_users(data)
        await message.answer(f"✅ Đã cộng {amount:,}đ cho ID {uid}")
    except:
        await message.answer("❌ Sai cú pháp.")
    await state.finish()

# --- 🔙 Quay Lại ---
@dp.message_handler(text="🔙 Quay Lại")
async def back(message: types.Message):
    is_admin = str(message.from_user.id) in ADMIN_IDS
    await message.answer("⬅️ Quay lại menu chính", reply_markup=main_keyboard(is_admin))

# --- RUN BOT ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
