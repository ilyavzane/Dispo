from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET


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


def decode_jwt_token(token):
    try:
        return int(jwt.decode(token, SECRET, algorithms=[ALGORITHM])["sub"])
    except (ValueError, KeyError):
        raise jwt.InvalidTokenError from None
