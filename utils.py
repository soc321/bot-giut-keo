import json

USERS_FILE = "users_data.json"

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open("users_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def reset_grab_counts_daily():
    users = load_users()
    for uid in users:
        users[uid]["grab_count"] = 5
    save_users(users)

def reset_recharge_weekly():
    users = load_users()
    for uid in users:
        users[uid]["recharged_this_week"] = 0
    save_users(users)
