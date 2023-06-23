import os

from dotenv import load_dotenv

load_dotenv()

TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')

