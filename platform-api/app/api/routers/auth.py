from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import create_token, get_current_user, verify_password
from app.core.db import db_cursor
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest) -> TokenResponse:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT username, password_hash, display_name, role
            FROM users
            WHERE username = %s AND enabled = TRUE
            """,
            (body.username,),
        )
        user = cur.fetchone()
        if user is None or not verify_password(body.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_token(user["username"], user["display_name"], user["role"])
    return TokenResponse(
        access_token=token,
        username=user["username"],
        display_name=user["display_name"],
        role=user["role"],
    )


@router.get("/me", response_model=UserInfo)
def get_me(user: dict = Depends(get_current_user)) -> UserInfo:
    return UserInfo(
        username=user["username"],
        display_name=user["display_name"],
        role=user["role"],
    )
