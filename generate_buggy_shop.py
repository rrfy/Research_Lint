#!/usr/bin/env python3
"""
BuggyShop - Project Generator
Генерирует все файлы для полнофункционального приложения с намеренными уязвимостями
"""

import os
import json
from pathlib import Path

# Все файлы проекта в виде словаря: путь -> содержимое

PROJECT_FILES = {
    # ==================== ИНИЦИАЛИЗАЦИЯ ====================
    "src/__init__.py": '"""\nBuggyShop - Учебное приложение с намеренными уязвимостями\n"""\n__version__ = "1.0.0"\n',
    
    "src/auth/__init__.py": '"""\nМодуль аутентификации\n"""\n',
    
    "src/products/__init__.py": '"""\nМодуль товаров\n"""\n',
    
    "src/orders/__init__.py": '"""\nМодуль заказов\n"""\n',
    
    "src/uploads/__init__.py": '"""\nМодуль загрузки файлов\n"""\n',
    
    "src/utils/__init__.py": '"""\nУтилиты\n"""\n',
    
    "tests/__init__.py": '"""\nТесты приложения\n"""\n',
    
    # ==================== КОНФИГ И БД ====================
    "src/config.py": '''"""
config.py - Конфигурация приложения
Дефекты: OWASP:A05 (5), OWASP:A02 (3), STYLES (4), SOLID:DIP (2), STRUCT (1)
"""
import os
from typing import Optional

# FIXME OWASP:A05 - Критичный конфиг хардкодирован
DEBUG = True  # FIXME OWASP:A05: Никогда не должно быть True в продакшене
SECRET_KEY = "very_secret_key_12345"  # FIXME OWASP:A02: Хардкод секрета
ALGORITHM = "HS256"  # FIXME STYLES: нижний регистр для константы (должен быть ALGORITHM)

# FIXME OWASP:A05 - Нет валидации переменных окружения
database_url = os.getenv("DATABASE_URL", "sqlite:///./buggy_shop.db")  # FIXME STYLES: camelCase вместо UPPER_CASE
DATABASE_URL = database_url

# FIXME OWASP:A02 - Пароли хранятся в памяти
DEFAULT_ADMIN_PASSWORD = "admin123"  # FIXME OWASP:A02: Пароль в коде

# FIXME OWASP:A05 - Нет ограничений на загрузку файлов
MAX_FILE_SIZE = 1000000000  # FIXME OWASP:A04: Слишком большой лимит (1GB)
UPLOAD_DIR = "uploads"  # FIXME STRUCT: должен быть в отдельной директории

# FIXME STYLES - Смешанные стили именования
JWT_EXPIRATION_HOURS = 24  # FIXME STYLES: snake_case смешивается с camelCase
jwtRefreshExpiration = 7 * 24  # FIXME STYLES: camelCase
accessTokenExpiry_hours = 1  # FIXME STYLES: смешанный стиль

# FIXME SOLID:DIP - Прямые зависимости от конкретных реализаций
CORS_ORIGINS = ["*"]  # FIXME OWASP:A05: ["*"] разрешает любые источники

# FIXME OWASP:A05 - SQL ошибки видны пользователю
SQL_ECHO = True  # FIXME OWASP:A05: Логирование SQL в продакшене

# FIXME SOLID:DIP - Конфиг не может быть переопределен
class Config:  # FIXME SOLID:DIP - класс невозможно расширить
    pass

# FIXME STYLES - Нет единообразия в объявлении переменных
PAGINATION_LIMIT = 100
paginationPageSize: int = 50  # FIXME STYLES: camelCase
DEFAULT_PAGE = 1  # FIXME STYLES: смешанные стили

# FIXME OWASP:A02 - Логирование в файл без ограничения размера
LOG_FILE = "app.log"  # FIXME OWASP:A05: Нет ротации логов
LOG_LEVEL = "debug"  # FIXME OWASP:A05: Debug в продакшене
''',

    "src/database.py": '''"""
database.py - Инициализация базы данных
Дефекты: OWASP:A03 (2), OWASP:A05 (3), STYLES (3), SOLID:SRP (2)
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL, SQL_ECHO

# FIXME OWASP:A05 - SQL эхо в продакшене раскрывает структуру БД
engine = create_engine(
    DATABASE_URL, 
    echo=SQL_ECHO,  # FIXME OWASP:A05: Логирование всех SQL запросов
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FIXME STYLES - Непоследовательная обработка ошибок
def get_db():
    """Получить сессию БД"""  # FIXME STYLES: docstring style
    db = SessionLocal()
    try:
        yield db
    except:  # FIXME OWASP:A09 - Пустой except ловит все исключения
        db.rollback()
    finally:
        db.close()

# FIXME SOLID:SRP - Слишком много обязанностей (инициализация, миграции, очистка)
def init_db():
    """Инициализировать БД с таблицами"""  # FIXME OWASP:A03 - Нет проверки существования таблиц
    # FIXME OWASP:A03 - Уязвимо к повторным инициализациям
    Base.metadata.create_all(bind=engine)
    
    # FIXME OWASP:A02 - Пароль администратора создается при инициализации
    db = SessionLocal()
    try:
        from auth.models import User
        from auth.services import hash_password  # FIXME SOLID:SRP - циклический импорт
        
        # FIXME OWASP:A01 - Администратор создается с предусмотренным паролем
        existing_admin = db.query(User).filter(User.email == "admin@buggyshop.com").first()
        if not existing_admin:
            admin = User(
                email="admin@buggyshop.com",
                username="admin",
                password_hash=hash_password("admin123"),  # FIXME OWASP:A02: Слабый пароль
                is_admin=True
            )
            db.add(admin)
            db.commit()
    except Exception as e:  # FIXME OWASP:A09 - Пустая обработка ошибок
        pass  # FIXME OWASP:A05: Ошибки инициализации игнорируются
    finally:
        db.close()

# FIXME OWASP:A05 - Нет проверки здоровья БД при запуске
def check_database_connection():
    """Проверить подключение к БД"""
    try:
        with engine.connect() as connection:
            pass  # FIXME STYLES: пустой блок
    except:  # FIXME OWASP:A09 - Пустой except
        raise  # FIXME OWASP:A05: Ошибки не логируются

# FIXME STYLES - Нет единообразия в функциях инициализации
def drop_all_tables():
    """Удалить все таблицы (для тестирования)"""
    # FIXME OWASP:A05 - Опасная функция доступна в продакшене
    Base.metadata.drop_all(bind=engine)
''',

    "src/main.py": '''"""
main.py - Главное приложение FastAPI
Дефекты: OWASP:A05 (5), OWASP:A01 (2), STYLES (4), SOLID:SRP (3)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from config import CORS_ORIGINS, DEBUG  # FIXME SOLID:SRP - прямой импорт конфига
from database import init_db

# FIXME OWASP:A05 - Инициализация с debug=True
app = FastAPI(
    title="BuggyShop API",
    description="Учебное приложение с намеренными уязвимостями",
    version="1.0.0",
    debug=DEBUG  # FIXME OWASP:A05: Debug режим доступен пользователям
)

# FIXME OWASP:A05 - CORS открыт для всех источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # FIXME OWASP:A05: ["*"] разрешает любые источники
    allow_credentials=True,  # FIXME OWASP:A05: Опасно с CORS_ORIGINS=["*"]
    allow_methods=["*"],  # FIXME OWASP:A05: Разрешены все методы
    allow_headers=["*"],  # FIXME OWASP:A05: Разрешены все заголовки
)

# FIXME OWASP:A04 - Нет валидации директории uploads
if not os.path.exists("uploads"):
    os.makedirs("uploads")  # FIXME OWASP:A04: Нет проверки прав доступа

# FIXME OWASP:A04 - Статические файлы открыты для всех
try:
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
except:  # FIXME OWASP:A09 - Пустой except
    pass

# FIXME STYLES - Импорты разбросаны, не упорядочены
from auth.routes import router as auth_router  # FIXME OWASP:A01 - Импорт после инициализации
from products.routes import router as products_router
from orders.routes import router as orders_router
from uploads.routes import router as uploads_router

# FIXME STYLES - Нет единообразия в регистрации маршрутов
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(
    products_router,  # FIXME STYLES - смешанный стиль форматирования
    prefix="/api/products",
    tags=["Products"]
)
app.include_router(orders_router, prefix="/api/orders", tags=["Orders"])
app.include_router(uploads_router, prefix="/api/uploads", tags=["Uploads"])

# FIXME OWASP:A05 - Информация о сервере доступна
@app.get("/")
def read_root():
    """Корневой эндпоинт"""
    return {
        "message": "BuggyShop API",
        "debug": DEBUG,  # FIXME OWASP:A05: Раскрытие режима debug
        "version": "1.0.0"
    }

# FIXME OWASP:A05 - Эндпоинт здоровья без аутентификации
@app.get("/health")
def health_check():  # FIXME STYLES: нет типов возврата
    """Проверка здоровья приложения"""
    return {"status": "ok"}

# FIXME OWASP:A09 - Обработчик ошибок слишком общий
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик исключений"""
    # FIXME OWASP:A05 - Стек трейс видим пользователю
    return {
        "error": str(exc),  # FIXME OWASP:A05: Полная информация об ошибке
        "type": type(exc).__name__,  # FIXME OWASP:A05: Тип исключения раскрыт
        "debug": DEBUG  # FIXME OWASP:A05: Информация о debug
    }

# FIXME OWASP:A05 - Инициализация при запуске без обработки ошибок
@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    try:
        init_db()
    except:  # FIXME OWASP:A09 - Пустой except скрывает ошибки
        print("DB init failed")  # FIXME OWASP:A05: print вместо логирования

if __name__ == "__main__":
    import uvicorn
    # FIXME OWASP:A05 - Жесткие параметры запуска
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # FIXME OWASP:A05: reload=True в продакшене
''',

    # ==================== AUTH МОДУЛЬ ====================
    "src/auth/models.py": '''"""
auth/models.py - ORM модели для аутентификации
Дефекты: OWASP:A01 (3), OWASP:A02 (4), SOLID:SRP (2), STYLES (2)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

# FIXME SOLID:SRP - Модель делает слишком много (валидация + логика)
class User(Base):
    """
    Модель пользователя
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)  # FIXME OWASP:A01 - Нет валидации email
    username = Column(String(100), unique=True, index=True)  # FIXME OWASP:A01 - Нет проверки длины
    password_hash = Column(String(255))  # FIXME OWASP:A02 - Нет проверки сложности пароля
    
    # FIXME OWASP:A01 - is_admin флаг может быть легко переключен
    is_admin = Column(Boolean, default=False)  # FIXME OWASP:A01: Нет логирования изменений
    
    # FIXME OWASP:A02 - История паролей не хранится
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # FIXME OWASP:A02 - Нет поля last_password_change для проверки срока действия
    # FIXME OWASP:A01 - Нет поля failed_login_attempts для блокировки
    
    def __repr__(self):  # FIXME STYLES: смешанные стили методов
        return f"<User {self.username}>"  # FIXME OWASP:A05 - Раскрытие информации
    
    # FIXME SOLID:SRP - Слишком много логики в модели
    def toDict(self):  # FIXME STYLES: camelCase вместо snake_case
        """Конвертировать в словарь"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "password": self.password_hash,  # FIXME OWASP:A02: Пароль в словаре!
            "isAdmin": self.is_admin,  # FIXME STYLES: camelCase
            "created_at": self.created_at
        }

# FIXME OWASP:A01 - Нет логирования административных действий
class AdminLog(Base):
    """Логирование административных действий"""
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer)
    action = Column(String(255))
    # FIXME OWASP:A05 - Логирование без ограничения размера
    timestamp = Column(DateTime, server_default=func.now())

# FIXME OWASP:A02 - Сессии не аннулируются
class UserSession(Base):
    """Модель сессии пользователя"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)  # FIXME OWASP:A01 - Нет внешнего ключа
    token = Column(String(500))  # FIXME OWASP:A02 - Токен хранится в открытом виде
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)  # FIXME OWASP:A02 - Нет проверки истечения
''',

    "src/auth/schemas.py": '''"""
auth/schemas.py - Pydantic схемы для валидации
Дефекты: OWASP:A01 (2), OWASP:A07 (3), STYLES (4), SOLID:ISP (2)
"""
from pydantic import BaseModel, Field, validator  # FIXME OWASP:A01 - Нет EmailStr
from typing import Optional

# FIXME SOLID:ISP - Большой интерфейс без разделения
class UserBase(BaseModel):
    """Базовая схема пользователя"""  # FIXME STYLES: doc и комментарий дублируют друг друга
    email: str  # FIXME OWASP:A01 - Нет валидации формата email
    username: str  # FIXME OWASP:A07 - Нет проверки на SQL-инъекции
    
class UserCreate(UserBase):
    """Схема создания пользователя"""  # FIXME STYLES: docstring style
    password: str  # FIXME OWASP:A07 - Пароль передается открытым текстом
    
    # FIXME OWASP:A07 - Валидация пароля слишком слабая
    @validator('password')
    def validate_password(cls, v):  # FIXME STYLES: cls вместо self
        """Валидировать пароль"""  # FIXME OWASP:A07 - Любой пароль принимается
        if len(v) < 3:  # FIXME OWASP:A07: Минимум 3 символа! (должно быть 12+)
            raise ValueError('Password too short')
        return v

class UserLogin(BaseModel):
    """Схема логина"""  # FIXME OWASP:A07 - Нет rate limiting validation
    username: str  # FIXME STYLES: нет Field описания
    password: str  # FIXME OWASP:A07 - Нет ограничения на длину

class UserResponse(BaseModel):
    """Схема ответа с пользователем"""
    id: int
    email: str
    username: str
    is_admin: bool  # FIXME OWASP:A01 - is_admin раскрыт в ответе
    
    # FIXME SOLID:ISP - Конфигурация смешана в схеме
    class Config:
        from_attributes = True  # FIXME STYLES: from_attributes вместо orm_mode
    
    # FIXME OWASP:A01 - Нет проверки прав доступа к полям

class TokenResponse(BaseModel):
    """Схема ответа с токеном"""
    access_token: str  # FIXME OWASP:A02 - Нет типа токена
    token_type: str = "bearer"  # FIXME STYLES: неправильно выбрана строка по умолчанию
    expires_in: Optional[int] = None  # FIXME OWASP:A07 - Время истечения необязательно
    # FIXME OWASP:A02 - Нет refresh токена

class UserUpdate(BaseModel):
    """Схема обновления пользователя"""  # FIXME SOLID:ISP - Использует все поля User
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None  # FIXME OWASP:A01 - Пользователь может сам себя сделать админом!
    
    @validator('email')
    def validate_email(cls, v):  # FIXME OWASP:A01 - Нет проверки на уникальность
        # FIXME OWASP:A01 - Любой email принимается
        return v

# FIXME STYLES - Нет разделения на публичные и приватные схемы
class AdminResponse(UserResponse):
    """Расширенная схема для администраторов"""
    is_admin: bool
    # FIXME OWASP:A01 - Админская схема доступна везде
''',

    "src/auth/services.py": '''"""
auth/services.py - Бизнес-логика аутентификации
Дефекты: OWASP:A01 (6), OWASP:A02 (8), OWASP:A03 (3), OWASP:A07 (6), STYLES (5), SOLID:SRP (4)
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from auth.models import User
from auth.schemas import UserCreate, UserLogin
import hashlib  # FIXME OWASP:A02 - Использование hashlib вместо bcrypt
import jwt  # FIXME OWASP:A07 - Старая версия python-jose
from config import SECRET_KEY, ALGORITHM, JWT_EXPIRATION_HOURS

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
''',

    "src/auth/dependencies.py": '''"""
auth/dependencies.py - FastAPI зависимости
Дефекты: OWASP:A01 (4), OWASP:A07 (3), STYLES (3), SOLID:DIP (2)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from auth.services import decode_token, get_user
from database import get_db

security = HTTPBearer()  # FIXME OWASP:A07 - Базовая схема безопасности

# FIXME OWASP:A07 - Зависимость без проверки токена
async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Получить текущего пользователя"""
    token = credentials.credentials
    payload = decode_token(token)  # FIXME OWASP:A07: Нет обработки None
    
    if payload is None:
        # FIXME OWASP:A07 - Исключение раскрывает информацию о токене
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {token}"  # FIXME OWASP:A05: Раскрытие токена в ошибке!
        )
    
    username = payload.get("sub")  # FIXME OWASP:A07 - Нет проверки наличия
    if not username:
        raise HTTPException(status_code=401, detail="Token invalid")
    
    user = get_user(db, username)  # FIXME OWASP:A07: Нет проверки существования
    
    if not user:
        # FIXME OWASP:A07 - Нет логирования попыток доступа
        raise HTTPException(status_code=401, detail="User not found")
    
    return user  # FIXME OWASP:A07: Нет проверки активного статуса

# FIXME OWASP:A01 - Проверка админа без должной защиты
async def get_admin_user(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Проверить, что пользователь администратор"""
    # FIXME OWASP:A01 - Нет логирования попыток доступа админов
    if not current_user.is_admin:
        # FIXME OWASP:A05 - Раскрытие информации о ролях
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {current_user.id} is not admin"  # FIXME OWASP:A05: Раскрытие ID
        )
    
    return current_user

# FIXME OWASP:A01 - Дополнительная проверка админа (дублирование)
def require_admin(user = Depends(get_current_user)):  # FIXME STYLES: нет типов
    """Требовать роль администратора"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user  # FIXME SOLID:DIP - Дублирование логики

# FIXME OWASP:A07 - Получение юзера по ID без авторизации
async def get_user_from_token(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Получить юзера из токена"""
    # FIXME OWASP:A07 - Нет проверки формата токена
    payload = decode_token(token.credentials)  # FIXME OWASP:A07: Возможен None
    
    if not payload:
        return None  # FIXME OWASP:A07: Молчаливое возвращение None
    
    user_id = payload.get("user_id")  # FIXME OWASP:A07: Нет проверки типа
    user = get_user(db, int(user_id))  # FIXME OWASP:A07: Возможен ValueError
    
    return user

# FIXME STYLES - Проверка владельца ресурса с неправильной сигнатурой
def check_owner(user_id: int, current_user = Depends(get_current_user)):  # FIXME STYLES: смешанные типы
    """Проверить, что пользователь владелец ресурса"""
    # FIXME OWASP:A01 - Админ всегда может пройти проверку
    if current_user.is_admin:  # FIXME OWASP:A01: Слишком широкие права админа
        return True  # FIXME STYLES: возвращает bool вместо user
    
    # FIXME OWASP:A01 - Сравнение без защиты
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not owner")
    
    return True
''',

    "src/auth/routes.py": '''"""
auth/routes.py - REST API маршруты для аутентификации
Дефекты: OWASP:A01 (5), OWASP:A07 (4), STYLES (5), SOLID:SRP (3)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from auth.models import User
from auth.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from auth.services import (
    register_user, 
    authenticate_user,
    create_access_token,
    get_user,
    update_user,
    delete_user,
    make_admin
)
from auth.dependencies import get_current_user, get_admin_user
from database import get_db
from config import JWT_EXPIRATION_HOURS

router = APIRouter()

# FIXME OWASP:A01 - Эндпоинт регистрации без ограничений
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""  # FIXME STYLES: опечатка в docstring
    # FIXME OWASP:A07 - Нет rate limiting
    # FIXME OWASP:A07 - Нет проверки на спам
    db_user = register_user(db, user)
    
    if not db_user:
        # FIXME OWASP:A07 - Возможна информация о существующем пользователе
        raise HTTPException(
            status_code=400,
            detail="User already registered"  # FIXME OWASP:A07: Раскрывает наличие пользователя
        )
    
    return db_user

# FIXME OWASP:A07 - Эндпоинт логина без защиты от brute force
@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Вход пользователя"""  # FIXME STYLES: нет подробного описания
    # FIXME OWASP:A07 - Нет rate limiting на попытки входа
    db_user = authenticate_user(db, user.username, user.password)
    
    if not db_user:
        # FIXME OWASP:A07 - Нет логирования неудачных попыток
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # FIXME OWASP:A07 - Нет проверки статуса пользователя (blocked/verified)
    access_token_expires = timedelta(hours=JWT_EXPIRATION_HOURS)
    access_token = create_access_token(
        data={"sub": db_user.username},  # FIXME OWASP:A07: sub должен быть ID, не username
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id  # FIXME OWASP:A05: Раскрытие ID пользователя
    }

# FIXME OWASP:A01 - Эндпоинт получения профиля без проверки доступа
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Получить профиль текущего пользователя"""  # FIXME STYLES: несоответствие нарратива
    return current_user

# FIXME OWASP:A01 - Эндпоинт получения любого пользователя по ID
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить пользователя по ID"""  # FIXME OWASP:A01 - Нет проверки доступа
    # FIXME OWASP:A01 - Любой залогиненный пользователь может получить данные
    user = get_user(db, user_id)  # FIXME OWASP:A01: Нет фильтрации данных
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # FIXME OWASP:A01 - Раскрытие информации о системе
    return user  # FIXME OWASP:A05: Вся информация открыта

# FIXME OWASP:A01 - Эндпоинт обновления другого пользователя
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user_endpoint(
    user_id: int,
    user_update,  # FIXME STYLES: нет типа параметра
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить пользователя"""
    # FIXME OWASP:A01 - Проверка доступа находится после чтения
    if current_user.id != user_id and not current_user.is_admin:  # FIXME OWASP:A01: Админ имеет доступ ко всем
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # FIXME OWASP:A01 - Пользователь может обновить is_admin для себя
    updated_user = update_user(db, user_id, **user_update.dict())  # FIXME OWASP:A01: Нет фильтрации полей
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user

# FIXME OWASP:A01 - Эндпоинт удаления пользователя
@router.delete("/users/{user_id}")
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить пользователя"""
    # FIXME OWASP:A01 - Проверка доступа недостаточна
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403)
    
    # FIXME OWASP:A01 - Нет подтверждения удаления
    success = delete_user(db, user_id)  # FIXME OWASP:A05: Нет логирования удаления
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    # FIXME STYLES - Пустой ответ
    return {}  # FIXME STYLES: Должен быть структурированный ответ

# FIXME OWASP:A01 - Функция изменения админа
@router.post("/admin/users/{user_id}/make-admin")
def make_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)  # FIXME OWASP:A01: Любой админ может дать права
):
    """Сделать пользователя администратором"""
    # FIXME OWASP:A01 - Нет логирования этого действия
    # FIXME OWASP:A05 - Нет ограничения на кол-во админов
    success = make_admin(db, user_id)  # FIXME OWASP:A01: Прямое изменение
    
    if not success:
        raise HTTPException(status_code=404)
    
    return {"message": "User is now admin"}

# FIXME OWASP:A01 - Эндпоинт списка всех пользователей
@router.get("/admin/users")
def list_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Получить список всех пользователей"""
    # FIXME OWASP:A05 - Нет пагинации
    # FIXME OWASP:A05 - Может быть DoS из-за больших данных
    users = db.query(User).all()  # FIXME OWASP:A01: Нет фильтрации
    
    # FIXME STYLES - Прямое возвращение моделей БД
    return users  # FIXME OWASP:A05: Раскрывает все поля

# FIXME OWASP:A07 - Эндпоинт смены пароля без защиты
@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Изменить пароль"""
    # FIXME OWASP:A07 - Параметры в query string вместо body
    # FIXME OWASP:A07 - История паролей не проверяется
    # FIXME OWASP:A02 - Нет валидации сложности нового пароля
    
    from auth.services import verify_password, hash_password  # FIXME STYLES: импорт в функции
    
    if not verify_password(old_password, current_user.password_hash):  # FIXME OWASP:A07: Нет rate limiting
        # FIXME OWASP:A07 - Нет логирования неудачных попыток
        raise HTTPException(status_code=401, detail="Wrong password")
    
    # FIXME OWASP:A02 - Пароль хешируется слабо (см. hash_password)
    current_user.password_hash = hash_password(new_password)  # FIXME OWASP:A02: Слабое хеширование
    
    try:
        db.commit()  # FIXME OWASP:A05 - Нет логирования изменения пароля
    except:  # FIXME OWASP:A09
        db.rollback()
        raise HTTPException(status_code=500)
    
    return {"message": "Password changed"}

# FIXME OWASP:A01 - Отладочный эндпоинт в продакшене
@router.get("/debug/token/{token}")
def debug_token(token: str):
    """Декодировать и показать содержимое токена"""  # FIXME OWASP:A05: Раскрытие токена!
    # FIXME OWASP:A01 - Эндпоинт доступен без аутентификации
    from auth.services import decode_token
    
    # FIXME OWASP:A05 - Раскрытие информации о токене
    payload = decode_token(token)  # FIXME OWASP:A07: Нет проверки validity
    
    if not payload:
        return {"error": "Invalid token"}
    
    # FIXME OWASP:A05 - Раскрытие всей информации из токена
    return payload  # FIXME OWASP:A05: Полное раскрытие payload

# FIXME STYLES - Разные форматы ответов в разных функциях
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):  # FIXME OWASP:A02: Токен не аннулируется
    """Логаут пользователя"""
    # FIXME OWASP:A02 - Logout не аннулирует токен
    # FIXME OWASP:A02 - Токен остается валидным
    return {"message": "Logged out"}  # FIXME STYLES: message вместо status

__all__ = ["router"]  # FIXME STYLES: __all__ в конце файла
''',
}

# Продолжу в следующем блоке...

def generate_files(base_path="buggy-shop"):
    """Генерировать все файлы проекта"""
    base = Path(base_path)
    
    # Создать директории
    created_dirs = set()
    for file_path in PROJECT_FILES.keys():
        dir_path = base / Path(file_path).parent
        if dir_path not in created_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            created_dirs.add(dir_path)
    
    # Создать файлы
    for file_path, content in PROJECT_FILES.items():
        file_full_path = base / file_path
        file_full_path.write_text(content, encoding='utf-8')
        print(f"✅ Created: {file_path}")
    
    print(f"\n✨ Создано {len(PROJECT_FILES)} файлов в {base_path}/")

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "buggy-shop"
    generate_files(path)
    print("\n🚀 Структура проекта создана успешно!")
    print(f"📂 Путь: {Path(path).absolute()}")
    print("\nСледующие шаги:")
    print("1. pip install -r requirements.txt")
    print("2. python -m uvicorn src.main:app --reload")
    print("3. Откройте http://localhost:8000/docs")
