from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard(is_admin=False):
    kb = [
        [KeyboardButton("💼 Đầu Tư"), KeyboardButton("💸 Rút Lãi")],
        [KeyboardButton("👤 Tài Khoản")]
    ]
    if is_admin:
        kb.append([KeyboardButton("⚙️ Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

admin_panel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📥 Danh Sách Nạp"), KeyboardButton("📤 Danh Sách Rút")],
        [KeyboardButton("🔙 Quay Lại")]
    ], resize_keyboard=True
)
