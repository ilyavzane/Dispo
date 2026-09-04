import os

from dotenv import load_dotenv

load_dotenv()
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
DATABASE_URL = os.getenv("DATABASE_URL")

SECRET = os.getenv("JWT_SECRET")

if not SECRET:
    raise RuntimeError("JWT SECRET is not given")

ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
