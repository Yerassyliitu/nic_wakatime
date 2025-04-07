import os
from dotenv import load_dotenv

load_dotenv()


API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "EMPTY_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1004@localhost:5432/nic_wakatime")
