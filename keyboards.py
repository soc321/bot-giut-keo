from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard(is_admin=False):
    kb = [
        [KeyboardButton("💼 Đầu Tư"), KeyboardButton("💸 Rút Lãi")],
        [KeyboardButton("💳 Nạp Tiền"), KeyboardButton("👤 Tài Khoản")]
    ]
    if is_admin:
        kb.append([KeyboardButton("⚙️ Admin Panel")])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(*[btn for row in kb for btn in row])

admin_panel_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("📥 Duyệt Nạp"),
    KeyboardButton("📊 Thống Kê"),
    KeyboardButton("🔙 Quay Lại")
)
