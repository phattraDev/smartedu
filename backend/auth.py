"""Simple JWT-based auth for the web dashboard."""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()  # looks in backend/ folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"), override=True)

SECRET_KEY = os.getenv("API_SECRET_KEY", "fallback-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def _get_users() -> dict:
    """Read credentials from env at call time, with explicit fallbacks."""
    username = os.environ.get("ADMIN_USERNAME") or "admin"
    password = os.environ.get("ADMIN_PASSWORD") or "admin123"
    return {
        username: {
            "password": password,
            "role": "admin",
        }
    }


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = _get_users().get(username.strip())
    if not user:
        return None
    if user["password"] != password.strip():
        return None
    return {"username": username.strip(), "role": user["role"]}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username, "role": payload.get("role", "teacher")}
    except JWTError:
        raise credentials_exception


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
