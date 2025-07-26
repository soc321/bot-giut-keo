import json
import os
from datetime import datetime, timedelta
from config import USER_DATA_FILE, INVESTMENTS, MIN_WITHDRAW, MAX_WITHDRAW

def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_or_create_user(user_id):
    user_id = str(user_id)
    data = load_users()
    if user_id not in data:
        data[user_id] = {
            "balance": 0,
            "investments": [],
            "withdrawals": [],
            "deposits": [],
            "bank": "",
            "bank_number": ""
        }
        save_users(data)
    return data[user_id]

def current_time():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def invest(user_id, amount):
    user_id = str(user_id)
    data = load_users()
    user = data[user_id]
    for g in INVESTMENTS:
        if g["amount"] == amount:
            inv = {
                "amount": amount,
                "daily": g["daily"],
                "days": g["days"],
                "start": datetime.now().strftime("%Y-%m-%d")
            }
            user["investments"].append(inv)
            save_users(data)
            return True
    return False

def calculate_profit(user_id):
    user_id = str(user_id)
    data = load_users()
    user = data[user_id]
    total_profit = 0
    now = datetime.now()
    for inv in user["investments"]:
        start_date = datetime.strptime(inv["start"], "%Y-%m-%d")
        elapsed_days = min((now - start_date).days + 1, inv["days"])
        total_profit += elapsed_days * inv["daily"]
    return total_profit

def withdraw(user_id, amount):
    user_id = str(user_id)
    data = load_users()
    user = data[user_id]
    profit_available = calculate_profit(user_id) - sum(w["amount"] for w in user["withdrawals"])
    if amount < MIN_WITHDRAW or amount > MAX_WITHDRAW or amount > profit_available:
        return False
    user["withdrawals"].append({
        "amount": amount,
        "time": current_time()
    })
    save_users(data)
    return True
