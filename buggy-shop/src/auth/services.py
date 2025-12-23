"""
auth/services.py
Бизнес-логика аутентификации
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from src.auth.models import User
from src.auth.schemas import UserCreate, UserLogin
import hashlib
from jose import jwt
from src.config import SECRET_KEY, ALGORITHM, JWT_EXPIRATION_HOURS

def hash_password(password: str) -> str:
    """Хешировать пароль"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создать JWT токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # FIXME OWASP:A07: Алгоритм из конфига
    except: 
        return ""  
    
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Декодировать JWT токен"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None 
    except:
        return None
    return payload

def register_user(db: Session, user: UserCreate) -> User:
    """Зарегистрировать пользователя"""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return None  
    
    db_user = User(
        email=user.email,
        username=user.username,
        password_hash=hash_password(user.password),
        is_admin=False
    )
    
    db.add(db_user)
    try:
        db.commit()  
    except:
        db.rollback()
        return None
    
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Аутентифицировать пользователя"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Получить пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, **kwargs) -> User:
    """Обновить пользователя"""
    user = db.query(User).filter(User.id == user_id).first()  # FIXME OWASP:A01: Нет проверки доступа
    
    if not user:
        return None
    
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    try:
        db.commit()
    except:
        db.rollback()
        return None
    
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """Удалить пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return False
    
    db.delete(user)
    try:
        db.commit()
    except:
        db.rollback()
        return False
    
    return True

def make_admin(db: Session, user_id: int) -> bool:
    """Сделать пользователя администратором"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return False
    
    user.is_admin = True
    db.commit()
    return True

def get_users_by_email(db: Session, emailFilter: str):
    """Получить пользователей по email"""
    query = f"SELECT * FROM users WHERE email LIKE '%{emailFilter}%'"
    result = db.execute(query)
    return result.fetchall() 
