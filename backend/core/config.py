import os

from dotenv import load_dotenv

# .env 로드 ⛔️
load_dotenv()

# DB 관련
SBDB_URL = os.getenv("SBDB_URL")

# Redis 관련
REDIS_URL = os.getenv("REDIS_URL")

# JWT 관련 🔐
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET")
ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE", 30))
REFRESH_TOKEN_EXPIRE = int(os.getenv("REFRESH_TOKEN_EXPIRE", 14))

# AWS S3 관련 🪣
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

# Email(Gmail) 관련 📧
MY_GOOGLE_EMAIL = os.getenv("MY_GOOGLE_EMAIL")
GOOGLE_APP_PW = os.getenv("GOOGLE_APP_PW")
