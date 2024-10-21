from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()
AVATARS_DIR = BASE_DIR.joinpath('/media/avatars/')

TEST_MODE = True
TEST_USER_ID = 7485502073

PORT = 5000
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://twif8-feb8a.web.app')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7396897324:AAHzNa_ncI4sf0hkg8M0txRt9KWZSnXFqC0')
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST', 'https://playcloud.pro')
WEBHOOK_PATH = 'webhook'
#ENGINE = "sqlite+aiosqlite:///./database/database.db"
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'qwerty'

ENGINE = f'postgresql+asyncpg://twif:twif@twif-postgres:5432/twif'