from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
ALGORITHM = "HS256"

def hash_password(password: str) -> str: return pwd_context.hash(password)
def verify_password(password: str, hashed: str) -> bool: return pwd_context.verify(password, hashed)
def create_access_token(subject: str, role: str) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": subject, "role": role, "exp": expiry}, settings.jwt_secret, algorithm=ALGORITHM)
def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.models.entities import User
    try: subject = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM]).get("sub")
    except JWTError: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = db.get(User, subject)
    if not user or not user.is_active: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Inactive user")
    return user
def require_roles(*roles: str):
    def check(user=Depends(current_user)):
        if user.role.name not in roles: raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return check
