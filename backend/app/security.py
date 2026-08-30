import bcrypt
import jwt
import os
from dotenv import load_dotenv
from datetime import timezone, timedelta, datetime

load_dotenv()
SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


# generating password hash that will be saved in database
def generate_hash(password: str) -> str:
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    return hashed_password.decode()


def check_password(entered_password: str, password_hash: str):
    return bcrypt.checkpw(entered_password.encode(), password_hash.encode())


def create_jwt_token(user_id: int):
    token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        SECRET,
        algorithm=ALGORITHM,
    )

    return token
