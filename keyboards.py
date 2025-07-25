from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS

def main_keyboard(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("👤 Tài Khoản"), KeyboardButton("🍬 Thả Kẹo" if user_id in ADMIN_IDS else ""))
    if user_id in ADMIN_IDS:
        kb.row(KeyboardButton("⚙️ Admin Cài Đặt"))
    return kb

def grab_candy_keyboard():
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton("🎯 Giật Hũ Kẹo", callback_data="grab_candy"))
    return ikb
