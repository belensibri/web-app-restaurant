from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import hashlib
from app.config import settings
from app.schemas.token import TokenData
from app.schemas.user import UserCreate
from app.repositories import user_repo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Pre-hash with SHA-256 to ensure we never hit the bcrypt 72-byte limit
    pre_hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return pwd_context.hash(pre_hashed)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Must use the same pre-hasher to verify
    pre_hashed = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return pwd_context.verify(pre_hashed, hashed_password)

def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.token_expire_minutes)
    to_encode = {"exp": expire, "user_id": user_id}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def decode_token(token: str) -> TokenData:
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise JWTError("User ID missing in token")
    return TokenData(user_id=user_id)

def register(db: Session, data: UserCreate):
    hashed_password = hash_password(data.password)
    return user_repo.create(
        db, 
        username=data.username,
        email=data.email,
        password_hash=hashed_password,
        full_name=data.full_name,
        role="waiter" # default role for registration
    )

def login(db: Session, username: str, password: str) -> str | None:
    user = user_repo.get_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return create_access_token(user.id)
