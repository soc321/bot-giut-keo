import json, time
from config import MIN_WITHDRAW, MAX_WITHDRAW

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

def get_or_create_user(user_id):
    data = load_users()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"deposits": [], "withdraws": []}
        save_users(data)
    return data[uid]

def calculate_profit(user_id):
    user = get_or_create_user(user_id)
    now = int(time.time())
    total_profit = 0
    for d in user["deposits"]:
        if d["status"] != "approved":
            continue
        days = (now - d["timestamp"]) // 86400
        rate = d.get("rate", 0)
        total_profit += d["amount"] * rate * days
    return round(total_profit)

def get_pending_deposits():
    data = load_users()
    result = []
    for uid, u in data.items():
        for d in u.get("deposits", []):
            if d["status"] == "pending":
                result.append((uid, d))
    return result
