import json
import os
from datetime import datetime, timedelta

DATA_FILE = "users_data.json"
INVESTMENTS = [
    {"amount": 5000, "days": 7, "daily_profit": 2000, "name": "Gói Trải Nghiệm"},
    {"amount": 20000, "days": 7, "daily_profit": 5000},
    {"amount": 50000, "days": 15, "daily_profit": 5000},
    {"amount": 100000, "days": 30, "daily_profit": 5000}
]

def load_users():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_or_create_user(user_id):
    data = load_users()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "balance": 0,
            "investments": [],
            "withdrawals": [],
            "deposits": [],
            "bank": "",
            "bank_number": ""
        }
        save_users(data)
    return data[uid]

def invest(user_id, amount):
    user = get_or_create_user(user_id)
    now = datetime.now().isoformat()
    for g in INVESTMENTS:
        if g["amount"] == amount:
            user["investments"].append({
                "amount": amount,
                "daily": g["daily_profit"],
                "start": now,
                "days": g["days"]
            })
            user["deposits"].append({"amount": amount, "time": now})
            save_users(load_users())
            return True
    return False

def calculate_profit(user_id):
    user = get_or_create_user(user_id)
    total_profit = 0
    today = datetime.now().date()
    for inv in user["investments"]:
        start = datetime.fromisoformat(inv["start"]).date()
        end = start + timedelta(days=inv["days"])
        if today > start:
            passed_days = min((today - start).days, inv["days"])
            earned = passed_days * inv["daily"]
            total_profit += earned
    return total_profit

def withdraw(user_id, amount):
    user = get_or_create_user(user_id)
    available = calculate_profit(user_id) - sum(w['amount'] for w in user["withdrawals"])
    if 7000 <= amount <= 500000 and amount <= available:
        user["withdrawals"].append({
            "amount": amount,
            "time": datetime.now().isoformat()
        })
        save_users(load_users())
        return True
    return False
