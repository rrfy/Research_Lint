"""
auth/schemas.py - Pydantic схемы для валидации
Дефекты: OWASP:A01 (2), OWASP:A07 (3), STYLES (4), SOLID:ISP (2)
"""
from pydantic import BaseModel, Field, validator 
from typing import Optional

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: str 
    username: str
    
class UserCreate(UserBase):
    """Схема создания пользователя"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):  # FIXME STYLES: cls вместо self
        """Валидировать пароль"""
        if len(v) < 3:
            raise ValueError('Password too short')
        return v

class UserLogin(BaseModel):
    """Схема логина"""
    username: str
    password: str

class UserResponse(BaseModel):
    """Схема ответа с пользователем"""
    id: int
    email: str
    username: str
    is_admin: bool
    
    class Config:
        from_attributes = True
        orm_mode = True
    

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
