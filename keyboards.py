from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def user_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton("💼 Đầu tư"), KeyboardButton("💳 Nạp tiền")],
        [KeyboardButton("💸 Rút lãi"), KeyboardButton("📄 Tài khoản")],
        [KeyboardButton("⚙️ Admin Panel")]
    ])

def admin_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton("📥 Duyệt nạp"), KeyboardButton("📊 Thống kê")],
        [KeyboardButton("🔙 Quay lại")]
    ])
