from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()
AVATARS_DIR = BASE_DIR.joinpath('/media/avatars/')

TEST_MODE = True
TEST_USER_ID = 749234118

WEBAPP_URL = 'https://8f9e-2a00-1fa2-425d-849a-b995-658f-cbaa-24ec.ngrok-free.app'
BOT_TOKEN = '7396897324:AAHzNa_ncI4sf0hkg8M0txRt9KWZSnXFqC0'
WEBHOOK_HOST = 'https://8f9e-2a00-1fa2-425d-849a-b995-658f-cbaa-24ec.ngrok-free.app'
WEBHOOK_PATH = 'webhook'
ENGINE = "sqlite+aiosqlite:///./database/database.db"
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'qwerty'
