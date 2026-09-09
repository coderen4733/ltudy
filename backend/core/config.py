import os

from dotenv import load_dotenv

# .env 로드 ⛔️
load_dotenv()

# DB 관련
DB_URL = os.getenv("DB_URL")
