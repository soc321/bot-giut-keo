import json
import random
from aiogram import types, Dispatcher
from config import ADMIN_IDS, MIN_GRAB, MAX_GRAB
from keyboards import grab_candy_keyboard
from utils import load_users, save_users

HU_FILE = "hu_keo.json"

def register_candy_handlers(dp: Dispatcher):
    dp.register_message_handler(throw_candy, text="🍬 Thả Kẹo")
    dp.register_callback_query_handler(grab_candy, lambda c: c.data.startswith("grab_"))

def get_hu():
    try:
        with open(HU_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def save_hu(data):
    with open(HU_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

async def throw_candy(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("❌ Chỉ admin được thả kẹo.")

    hu_data = {
        "amount": random.randint(MIN_GRAB, MAX_GRAB),
        "grabbed": False,
        "user_id": None
    }
    save_hu(hu_data)
    kb = grab_candy_keyboard()
    await message.answer(f"🍭 Hũ kẹo {hu_data['amount']:,} đã được thả!\nAi sẽ là người giật được?", reply_markup=kb)

async def grab_candy(callback: types.CallbackQuery):
    users = load_users()
    uid = str(callback.from_user.id)

    if uid not in users:
        users[uid] = {"balance": 0, "grab_count": 5, "bank": "", "recharged_this_week": 0}

    if users[uid]["grab_count"] <= 0:
        return await callback.answer("❌ Hết lượt giật!", show_alert=True)

    if users[uid]["recharged_this_week"] < 5000 and callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("⚠️ Bạn cần nạp ít nhất 5,000 điểm mỗi tuần để giật kẹo!", show_alert=True)

    hu = get_hu()
    if not hu or hu["grabbed"]:
        return await callback.answer("❌ Hũ kẹo không còn!", show_alert=True)

    hu["grabbed"] = True
    hu["user_id"] = uid
    save_hu(hu)

    users[uid]["balance"] += hu["amount"]
    users[uid]["grab_count"] -= 1
    save_users(users)

    await callback.message.edit_text(f"🎉 <b>{callback.from_user.full_name}</b> đã giật được {hu['amount']:,} điểm!")
    await callback.answer()
