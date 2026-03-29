from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.auth.models import User
from src.auth.services import decode_token, get_user
from src.database import get_db


security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {token}",
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Token invalid")

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

async def get_admin_user(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {current_user.id} is not admin"
        )
    return current_user


def require_admin(user = Depends(get_current_user)): 
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user 

async def get_user_from_token(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):

    payload = decode_token(token.credentials)
    if not payload:
        return None 
    
    user_id = payload.get("user_id")
    user = get_user(db, int(user_id))
    
    return user

def check_owner(user_id: int, current_user = Depends(get_current_user)):
    if current_user.is_admin:
        return True

    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not owner")
    
    return True
