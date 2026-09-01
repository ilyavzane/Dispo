from fastapi.security import HTTPBearer
from fastapi import Depends
from app.security import decode_jwt_token
from app.repository import get_user_by_id
from fastapi import HTTPException
import jwt

bearer_scheme = HTTPBearer(auto_error=False)


async def require_admin(token=Depends(bearer_scheme)):
    try:
        if token is None:
            raise HTTPException(status_code=401, detail="No token provided")

        user_id = decode_jwt_token(token.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired jwt token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_data = await get_user_by_id(user_id)

    if user_data is None:
        raise HTTPException(status_code=401, detail="User not found")

    user_role = user_data["role"]
    user_status = user_data["status"]

    if user_role != "admin" or user_status != "approved":
        raise HTTPException(status_code=403, detail="You don't have rights")
