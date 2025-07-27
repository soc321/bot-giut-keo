from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Nạp tiền"), KeyboardButton(text="📤 Rút tiền")],
        [KeyboardButton(text="📄 Tài khoản")],
    ],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📥 Duyệt nạp")],
        [KeyboardButton(text="🏠 Về menu")],
    ],
    resize_keyboard=True
)
