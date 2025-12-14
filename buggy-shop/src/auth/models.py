"""
auth/models.py - ORM модели для аутентификации
Дефекты: OWASP:A01 (3), OWASP:A02 (4), SOLID:SRP (2), STYLES (2)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from src.database import Base

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
