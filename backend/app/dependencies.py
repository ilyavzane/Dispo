import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

from app.enums import Roles, Statuses
from app.repositories.users import get_user_by_id
from app.security import decode_jwt_token

bearer_scheme = HTTPBearer(auto_error=False)


def require_role(*roles):
    async def check(token=Depends(bearer_scheme)):
        try:
            if token is None:
                raise HTTPException(status_code=401, detail="No token provided")

            user_id = decode_jwt_token(token.credentials)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Expired jwt token") from None
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token") from None

        user_data = await get_user_by_id(user_id)

        if user_data is None:
            raise HTTPException(status_code=401, detail="User not found")

        user_role = user_data["role"]
        user_status = user_data["status"]

        if user_role not in [*roles, Roles.ADMIN] or user_status != Statuses.APPROVED:
            raise HTTPException(status_code=403, detail="You don't have rights")

        return user_data

    return check
