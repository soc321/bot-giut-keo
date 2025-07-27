import json
from config import USERS_FILE

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_user(user_id):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "balance": 0,
            "invested": 0,
            "bank": "",
            "account": "",
            "name": "",
        }
        save_users(users)
    return users[str(user_id)]

def update_user(user_id, key, value):
    users = load_users()
    users[str(user_id)][key] = value
    save_users(users)

def increase_balance(user_id, amount):
    users = load_users()
    users[str(user_id)]["balance"] += amount
    save_users(users)

def decrease_balance(user_id, amount):
    users = load_users()
    users[str(user_id)]["balance"] -= amount
    save_users(users)

def auto_add_interest():
    users = load_users()
    for uid, data in users.items():
        lãi = data["invested"] * 0.05  # 5%/ngày
        data["balance"] += int(lãi)
    save_users(users)
