from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN not set in .env")

DATA_FILE = os.getenv("DATA_FILE", "bot_data.json")

# ADMIN_IDS можно задавать в .env как "123,456", или оставить дефолт
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "563057258").split(",") if x.strip()]
