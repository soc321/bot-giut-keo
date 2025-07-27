import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8121092898:AAG2FjMFjP1rjBWkaSSl_PpiMGee0StjuGg")
ADMIN_IDS = [int(i) for i in os.getenv("6730559072", "").split(",") if i]

USERS_FILE = "users.json"
