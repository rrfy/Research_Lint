"""
auth/services.py - Бизнес-логика аутентификации
Дефекты: OWASP:A01 (6), OWASP:A02 (8), OWASP:A03 (3), OWASP:A07 (6), STYLES (5), SOLID:SRP (4)
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from src.auth.models import User
from src.auth.schemas import UserCreate, UserLogin
import hashlib  # FIXME OWASP:A02 - Использование hashlib вместо bcrypt
from jose import jwt  # FIXME OWASP:A07 - Старая версия python-jose
from src.config import SECRET_KEY, ALGORITHM, JWT_EXPIRATION_HOURS

# FIXME OWASP:A02 - Нет использования bcrypt
def hash_password(password: str) -> str:
    """Хешировать пароль"""  # FIXME OWASP:A02 - Использует простой hashlib
    # FIXME OWASP:A02 - Нет соли
    return hashlib.sha256(password.encode()).hexdigest()  # FIXME OWASP:A02: SHA256 для паролей!

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    # FIXME OWASP:A02 - Уязвимо к timing attack
    return hash_password(plain_password) == hashed_password  # FIXME OWASP:A02: Уязвимое сравнение

# FIXME OWASP:A07 - JWT создание без проверок
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создать JWT токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    # FIXME OWASP:A02 - Нет проверки типов данных
    to_encode.update({"exp": expire})  # FIXME OWASP:A07 - Нет обработки ошибок при кодировании
    
    # FIXME OWASP:A07 - Нет проверки SECRET_KEY
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # FIXME OWASP:A07: Алгоритм из конфига
    except:  # FIXME OWASP:A09 - Пустой except
        return ""  # FIXME OWASP:A07: Молчаливое возвращение пустой строки
    
    return encoded_jwt

# FIXME OWASP:A07 - Декодирование JWT без проверок
def decode_token(token: str) -> dict:
    """Декодировать JWT токен"""
    try:
        # FIXME OWASP:A07 - Нет обработки истечения токена
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # FIXME OWASP:A07: Нет verify
        username: str = payload.get("sub")  # FIXME OWASP:A07: Нет проверки наличия
        if username is None:
            return None  # FIXME OWASP:A07: Нет логирования
    except:  # FIXME OWASP:A09 - Пустой except ловит все
        # FIXME OWASP:A05 - Ошибка JWT раскрывается
        return None
    return payload

# FIXME OWASP:A01 - Функция без аутентификации
def register_user(db: Session, user: UserCreate) -> User:
    """Зарегистрировать пользователя"""
    # FIXME OWASP:A03 - Уязвимо к SQL-инъекции при email
    existing_user = db.query(User).filter(User.email == user.email).first()
    # FIXME OWASP:A01 - Нет защиты от перебора (timing attack)
    if existing_user:
        return None  # FIXME OWASP:A07: Нет специального исключения
    
    # FIXME OWASP:A02 - Пароль хешируется слабо
    db_user = User(
        email=user.email,
        username=user.username,
        password_hash=hash_password(user.password),
        is_admin=False
    )
    
    db.add(db_user)
    try:
        db.commit()  # FIXME OWASP:A05 - Нет логирования регистрации
    except:  # FIXME OWASP:A09 - Пустой except
        db.rollback()
        return None
    
    db.refresh(db_user)
    return db_user

# FIXME OWASP:A07 - Функция без rate limiting
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Аутентифицировать пользователя"""
    # FIXME OWASP:A03 - Прямое внедрение username в запрос (SQL-инъекция)
    user = db.query(User).filter(User.username == username).first()
    
    # FIXME OWASP:A01 - Нет логирования попыток входа
    if not user:
        # FIXME OWASP:A07 - Timing attack: разное время для существующего/несуществующего пользователя
        return None
    
    # FIXME OWASP:A02 - Проверка пароля уязвима к timing attack
    if not verify_password(password, user.password_hash):
        return None
    
    # FIXME OWASP:A01 - Нет проверки, заблокирован ли пользователь
    return user

# FIXME OWASP:A01 - Получение пользователя по ID без проверок
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Получить пользователя по ID"""
    # FIXME OWASP:A01 - Нет проверки, может ли текущий юзер это делать
    return db.query(User).filter(User.id == user_id).first()

# FIXME OWASP:A01 - Обновление пользователя без проверок доступа
def update_user(db: Session, user_id: int, **kwargs) -> User:
    """Обновить пользователя"""
    user = db.query(User).filter(User.id == user_id).first()  # FIXME OWASP:A01: Нет проверки доступа
    
    if not user:
        return None
    
    # FIXME OWASP:A01 - Можно обновить is_admin напрямую
    for key, value in kwargs.items():
        if hasattr(user, key):  # FIXME OWASP:A01: Нет whitelist полей
            # FIXME OWASP:A01 - is_admin обновляется без проверок
            setattr(user, key, value)
    
    try:
        db.commit()  # FIXME OWASP:A05 - Нет логирования изменений
    except:  # FIXME OWASP:A09
        db.rollback()
        return None
    
    db.refresh(user)
    return user

# FIXME OWASP:A01 - Удаление пользователя без аутентификации
def delete_user(db: Session, user_id: int) -> bool:
    """Удалить пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return False
    
    # FIXME OWASP:A01 - Нет проверки прав
    db.delete(user)  # FIXME OWASP:A05 - Нет логирования удаления
    try:
        db.commit()
    except:  # FIXME OWASP:A09
        db.rollback()
        return False
    
    return True

# FIXME OWASP:A01 - Функция для изменения прав без проверок
def make_admin(db: Session, user_id: int) -> bool:
    """Сделать пользователя администратором"""
    # FIXME OWASP:A01 - Нет проверки текущего администратора
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return False
    
    # FIXME OWASP:A01 - Логирование отсутствует или неадекватно
    user.is_admin = True
    db.commit()  # FIXME OWASP:A01: Прямое изменение без проверок
    return True

# FIXME OWASP:A03 - Получение всех пользователей с SQL-инъекцией
def get_users_by_email(db: Session, emailFilter: str):  # FIXME STYLES: camelCase
    """Получить пользователей по email"""
    # FIXME OWASP:A03 - ОПАСНО: прямое внедрение в SQL!
    query = f"SELECT * FROM users WHERE email LIKE '%{emailFilter}%'"  # FIXME OWASP:A03: SQL-инъекция!
    # FIXME STYLES - Неправильное использование ORM
    result = db.execute(query)  # FIXME OWASP:A03: execute вместо query builder
    return result.fetchall()  # FIXME OWASP:A03: Результат не типизирован
