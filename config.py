from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()
AVATARS_DIR = BASE_DIR.joinpath('/media/avatars/')

TEST_MODE = True
TEST_USER_ID = 7485502073

PORT = 4550
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://192.168.0.8:5173')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '5166691505:AAEbw80sx5EGT7pB9eT954PTO3WtowUMEME')
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST', 'https://d8cd-2a00-1fa2-120-bf9b-61ef-3d33-292e-1d69.ngrok-free.app')
WEBHOOK_PATH = 'webhook'
#ENGINE = "sqlite+aiosqlite:///./database/database.db"
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'qwerty'

ENGINE = f'postgresql+asyncpg://twif:twif@twif-postgres:5432/twif'