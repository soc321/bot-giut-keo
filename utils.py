import json, os
from datetime import datetime
from config import MIN_WITHDRAW, MAX_WITHDRAW

DATA_FILE = "users.json"

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_or_create_user(user_id, data=None):
    user_id = str(user_id)
    if data is None:
        data = load_users()
    if user_id not in data:
        data[user_id] = {
            "balance": 0,
            "bank": "-",
            "bank_number": "-",
            "investments": [],
            "deposits": [],
            "withdrawals": []
        }
    return data[user_id]

def invest(user_id, package):
    data = load_users()
    user = get_or_create_user(user_id, data)
    user["balance"] -= package["amount"]
    user["investments"].append({
        "amount": package["amount"],
        "daily": package["daily"],
        "days": package["days"],
        "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_users(data)

def calculate_profit(user_id):
    user = get_or_create_user(user_id)
    total = 0
    now = datetime.now()
    for inv in user["investments"]:
        start = datetime.strptime(inv["start"], "%Y-%m-%d %H:%M:%S")
        days_passed = (now - start).days
        earn_days = min(days_passed, inv["days"])
        total += earn_days * inv["daily"]
    return total

def withdraw(user_id, amount):
    data = load_users()
    user = get_or_create_user(user_id, data)
    profit = calculate_profit(user_id)
    withdrawn = sum(w["amount"] for w in user["withdrawals"])
    available = profit - withdrawn
    if amount < MIN_WITHDRAW or amount > MAX_WITHDRAW or amount > available:
        return False
    user["withdrawals"].append({
        "amount": amount,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_users(data)
    return True
