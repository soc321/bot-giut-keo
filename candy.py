from aiogram import types
from keyboards import grab_candy_keyboard
from aiogram.dispatcher import Dispatcher
from config import ADMIN_ID, MIN_CANDY_POINT, MAX_CANDY_POINT
from keyboards import grab_candy_keyboard
from utils import load_json, save_json
import random
from datetime import datetime

def register_candy_handlers(dp: Dispatcher):
    @dp.message_handler(lambda m: m.text == "🍬 Thả Kẹo")
    async def drop_candy(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return await msg.reply("❌ Bạn không có quyền sử dụng chức năng này.")

        candy_data = load_json("candy_data.json")
        candy_id = str(len(candy_data) + 1)
        num_portions = random.randint(2, 6)
        candy_value = random.randint(MIN_CANDY_POINT, MAX_CANDY_POINT)

        candy_data[candy_id] = {
            "value": candy_value,
            "grabbed": 0,
            "max_grabs": num_portions,
            "grabbers": []
        }
        save_json("candy_data.json", candy_data)

        text = f"🍭 Hũ kẹo mới vừa được thả!\n🎁 Nhấn để giựt kẹo [{0}/{num_portions}]"
        await msg.answer(text, reply_markup=grab_candy_keyboard(candy_id))

    @dp.callback_query_handler(lambda c: c.data.startswith("grab_"))
    async def grab_candy(callback: types.CallbackQuery):
        user_id = str(callback.from_user.id)
        users = load_json("users_data.json")
        candy_data = load_json("candy_data.json")
        cid = callback.data.split("_")[1]

        if cid not in candy_data:
            return await callback.answer("❌ Hũ kẹo không tồn tại.", show_alert=True)

        candy = candy_data[cid]
        if user_id in candy["grabbers"]:
            return await callback.answer("🍬 Bạn đã giựt hũ kẹo này rồi!", show_alert=True)

        user = users.get(user_id)
        if not user:
            users[user_id] = {
                "balance": 0,
                "daily_grabs": 0,
                "bank": "",
                "ref": None,
                "recharged": 0,
                "can_grab": False
            }
            user = users[user_id]

        today = datetime.now().date()
        last_grab = user.get("last_grab")
        if last_grab != str(today):
            user["daily_grabs"] = 0
            user["last_grab"] = str(today)

        if not user.get("can_grab", False):
            return await callback.answer("❌ Bạn cần nạp ít nhất 5000 điểm trong tuần để giựt kẹo.", show_alert=True)

        if user["daily_grabs"] >= 5:
            return await callback.answer("⛔ Bạn đã hết lượt giựt hôm nay.", show_alert=True)

        if candy["grabbed"] >= candy["max_grabs"]:
            return await callback.answer("❌ Hũ kẹo đã bị giựt hết.", show_alert=True)

        reward = round(candy["value"] / candy["max_grabs"])
        user["balance"] += reward
        user["daily_grabs"] += 1
        candy["grabbed"] += 1
        candy["grabbers"].append(user_id)

        save_json("users_data.json", users)
        save_json("candy_data.json", candy_data)

        new_text = f"🍭 Hũ kẹo mới vừa được thả!\n🎁 Nhấn để giựt kẹo [{candy['grabbed']}/{candy['max_grabs']}]"
        try:
            await callback.message.edit_text(new_text, reply_markup=grab_candy_keyboard(cid))
        except:
            pass

        await callback.answer(f"🎉 Bạn đã giựt được {reward} điểm!", show_alert=True)
