from fastapi import Depends, Request
from fastapi.exceptions import HTTPException

from database import database
from security import decode_jwt_token


async def get_request_user(request: Request) -> tuple:
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        user_info = decode_jwt_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")

    print(user_info)
    user = await database.select("users", ["id", "username"], f"id = '{user_info["user_id"]}'", single=True)

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user
