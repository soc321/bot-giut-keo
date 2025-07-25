import json
import os
import json
from datetime import datetime

USERS_FILE = "users_data.json"

def reset_grab_counts_daily():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)

        for user_id in users:
            users[user_id]["grab_count"] = 5  # đặt lại 5 lượt mỗi ngày

        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error resetting daily grab counts: {e}")

def reset_recharge_weekly():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)

        for user_id in users:
            users[user_id]["recharged_this_week"] = 0

        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error resetting weekly recharge: {e}")

def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_and_reset_weekly(user):
    now = datetime.now()
    last_recharge = user.get("last_recharge")
    if last_recharge:
        last_time = datetime.strptime(last_recharge, "%Y-%m-%d")
        if (now - last_time).days >= 7:
            user["can_grab"] = False
            user["daily_grabs"] = 0
    return user
