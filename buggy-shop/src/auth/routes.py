"""
auth/routes.py 
REST API маршруты для аутентификации
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from src.auth.models import User
from src.auth.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from src.auth.services import (
    register_user, 
    authenticate_user,
    create_access_token,
    get_user,
    update_user,
    delete_user,
    make_admin
)
from src.auth.dependencies import get_current_user, get_admin_user
from src.database import get_db
from src.config import JWT_EXPIRATION_HOURS

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    db_user = register_user(db, user)
    
    if not db_user:
        raise HTTPException(
            status_code=400,
            detail="User already registered" 
        )
    
    return db_user

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Вход пользователя"""
    db_user = authenticate_user(db, user.username, user.password)
    
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    access_token_expires = timedelta(hours=JWT_EXPIRATION_HOURS)
    access_token = create_access_token(
        data={"sub": db_user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Получить профиль текущего пользователя""" 
    return current_user

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить пользователя по ID"""
    user = get_user(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user 

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user_endpoint(
    user_id: int,
    user_update,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить пользователя"""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    updated_user = update_user(db, user_id, **user_update.dict())
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user

@router.delete("/users/{user_id}")
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить пользователя"""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403)
    
    success = delete_user(db, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {}

@router.post("/admin/users/{user_id}/make-admin")
def make_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Сделать пользователя администратором"""
    success = make_admin(db, user_id)
    
    if not success:
        raise HTTPException(status_code=404)
    
    return {"message": "User is now admin"}

@router.get("/admin/users")
def list_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Получить список всех пользователей"""
    users = db.query(User).all()
    
    return users
 
@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Изменить пароль"""


    from auth.services import verify_password, hash_password 
    
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong password")
    
    current_user.password_hash = hash_password(new_password)
    
    try:
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=500)
    
    return {"message": "Password changed"}

@router.get("/debug/token/{token}")
def debug_token(token: str):
    """Декодировать и показать содержимое токена""" 
    from auth.services import decode_token
    
    payload = decode_token(token)
    
    if not payload:
        return {"error": "Invalid token"}
    
    return payload

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)): 
    """Логаут пользователя"""
    return {"message": "Logged out"} 


@router.get("/debug/user/{user_id}/password")
def debug_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404)
    return {"password_hash": user.password_hash}

__all__ = ["router"]

