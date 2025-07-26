import json
import os
from datetime import datetime
from threading import Lock
from config import MIN_WITHDRAW, MAX_WITHDRAW

DATA_FILE = "users_data.json"
_lock = Lock()

def load_users():
    with _lock:
        if not os.path.exists(DATA_FILE):
            return {}
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(data):
    with _lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def get_or_create_user(user_id):
    uid = str(user_id)
    data = load_users()
    if uid not in data:
        data[uid] = {
            "balance": 0,
            "investments": [],
            "withdrawals": [],
            "deposits": [],
            "bank": "-",
            "bank_number": "-",
            "last_profit_check": current_time()
        }
        save_users(data)
    return data, data[uid]

def invest(user_id, package):
    data, user = get_or_create_user(user_id)
    user["investments"].append({
        "amount": package["amount"],
        "daily": package["daily"],
        "days": package["days"],
        "start": current_time()
    })
    save_users(data)

def calculate_profit(user_id):
    _, user = get_or_create_user(user_id)
    now = datetime.now()
    total = 0
    for inv in user["investments"]:
        start = datetime.strptime(inv["start"], "%Y-%m-%d %H:%M:%S")
        elapsed_days = (now - start).days
        earn_days = min(elapsed_days, inv["days"])
        total += earn_days * inv["daily"]
    return total

def withdraw(user_id, amount):
    data, user = get_or_create_user(user_id)
    profit = calculate_profit(user_id)
    withdrawn = sum(w["amount"] for w in user["withdrawals"])
    available = profit - withdrawn
    if amount < MIN_WITHDRAW or amount > MAX_WITHDRAW or amount > available:
        return False
    user["withdrawals"].append({
        "amount": amount,
        "time": current_time()
    })
    save_users(data)
    return True

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_money(amount):
    return "{:,}đ".format(amount)
