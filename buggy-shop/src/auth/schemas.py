"""
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
        orm_mode = True
    
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
