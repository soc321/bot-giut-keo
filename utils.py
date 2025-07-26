import json
import os
import time

DATA_FILE = "users.json"

def load_users():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_or_create_user(user_id: str):
    data = load_users()
    if user_id not in data:
        data[user_id] = {
            "balance": 0,
            "deposits": [],
            "investments": [],
            "bank": "",
            "profit": 0
        }
        save_users(data)
    return data[user_id]

def calculate_profit(user_id):
    data = load_users()
    user = get_or_create_user(data, user_id)
    total_profit = 0
    now = int(time.time())

    for inv in user["investments"]:
        elapsed_days = (now - inv["start_time"]) // 86400
        days = min(inv["duration"], elapsed_days)
        total_profit += days * inv["daily_profit"]

    return total_profit
