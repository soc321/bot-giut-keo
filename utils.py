import json
import os
from datetime import datetime

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