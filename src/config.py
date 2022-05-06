from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    '''Bot configuration'''

    BOT_TOKEN = getenv("BOT_TOKEN")
    LOG_CHANNEL = int(getenv("LOG_CHANNEL"))
    HELP_CHANNEL = int(getenv("HELP_CHANNEL"))
    ADMIN_ROLE = int(getenv("ADMIN_ROLE"))
    STAFF_ROLE = int(getenv("STAFF_ROLE"))
