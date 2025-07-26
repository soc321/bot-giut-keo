from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard(is_admin=False):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("💼 Đầu Tư"), KeyboardButton("💸 Rút Lãi"))
    kb.row(KeyboardButton("💳 Nạp Tiền"), KeyboardButton("👤 Tài Khoản"))
    if is_admin:
        kb.add(KeyboardButton("⚙️ Admin Panel"))
    return kb

admin_panel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel_kb.row(KeyboardButton("📥 Duyệt Nạp"), KeyboardButton("📊 Thống Kê"))
admin_panel_kb.add(KeyboardButton("🔙 Quay Lại"))
