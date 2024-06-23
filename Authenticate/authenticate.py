import time
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from database.connection import Settings

SECRET_KEY: Optional[str] = None
settings = Settings()


def create_token(user: str):
    payload = {
        "user": user,
        "expires": time.time() + 1800
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token: str):
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        expire = data.get("expires")

        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied"
            )
        if time.time() > expire:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token Expired"
            )
        return data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/signin")

async def authenticate(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access"
        )
    decoded_token = verify_token(token)
    return decoded_token["user"]
