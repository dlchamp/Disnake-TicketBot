import os
from dotenv import load_dotenv

load_dotenv()

"""
BOT CONFIG FILE
Update values in .env file
"""

BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))
HELP_CHANNEL = int(os.getenv("HELP_CHANNEL"))
OWNER_ID = int(os.getenv("OWNER_ID"))
ADMIN_ROLE = int(os.getenv("ADMIN_ROLE"))
STAFF_ROLE = int(os.getenv("STAFF_ROLE"))
