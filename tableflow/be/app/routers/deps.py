from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import decode_token
from app.repositories import user_repo

bearer_scheme = HTTPBearer()

def get_current_user(creds=Depends(bearer_scheme), db: Session = Depends(get_db)):
    try:
        token_data = decode_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    if token_data.user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = user_repo.get_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    return user
