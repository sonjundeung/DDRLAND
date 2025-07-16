import os
from dotenv import load_dotenv

# .env 파일 자동 로딩 (프로젝트 루트에 위치)
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
BOT_USERNAME = os.getenv("BOT_USERNAME")
