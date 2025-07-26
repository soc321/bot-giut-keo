from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("📦 Đầu Tư"), KeyboardButton("💸 Rút Lãi"))
main_menu.add(KeyboardButton("📊 Thống Kê"), KeyboardButton("📥 Duyệt Nạp"))

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.add(KeyboardButton("📥 Duyệt Nạp"), KeyboardButton("📊 Thống Kê"))
admin_menu.add(KeyboardButton("⬅️ Quay Lại"))

back_menu = ReplyKeyboardMarkup(resize_keyboard=True)
back_menu.add(KeyboardButton("⬅️ Quay Lại"))
