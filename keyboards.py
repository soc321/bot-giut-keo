from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard(is_admin=False):
    kb = [
        [KeyboardButton(text="💼 Đầu Tư"), KeyboardButton(text="💸 Rút Lãi")],
        [KeyboardButton(text="💳 Nạp Tiền"), KeyboardButton(text="👤 Tài Khoản")],
    ]
    if is_admin:
        kb.append([KeyboardButton(text="⚙️ Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

admin_panel_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📥 Duyệt Nạp"), KeyboardButton(text="📊 Thống Kê")],
    [KeyboardButton(text="🔙 Quay Lại")]
], resize_keyboard=True)
