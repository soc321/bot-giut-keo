from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu(is_admin=False):
    kb = [
        [KeyboardButton("👤 Tài khoản"), KeyboardButton("🎁 Giựt hũ kẹo")],
        [KeyboardButton("🔗 Mời bạn bè"), KeyboardButton("💸 Rút điểm")],
    ]
    if is_admin:
        kb.append([KeyboardButton("⚙️ Quản trị")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)