from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Các bàn phím khác ở đây...
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(KeyboardButton("👤 Tài Khoản"))
# v.v...

# Thêm HÀM NÀY vào cuối file:
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def grab_candy_keyboard(candy_id: str, grabbed: int, total: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    button_text = f"🚀 Giựt Hũ Kẹo [{grabbed}/{total}]"
    button = InlineKeyboardButton(text=button_text, callback_data=f"grab_candy:{candy_id}")
    keyboard.add(button)
    return keyboard
def main_menu(is_admin=False):
    kb = [
        [KeyboardButton("👤 Tài khoản"), KeyboardButton("🎁 Giựt hũ kẹo")],
        [KeyboardButton("🔗 Mời bạn bè"), KeyboardButton("💸 Rút điểm")],
    ]
    if is_admin:
        kb.append([KeyboardButton("⚙️ Quản trị")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
