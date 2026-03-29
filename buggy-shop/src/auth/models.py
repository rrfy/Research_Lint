from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from src.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True) 
    password_hash = Column(String(255))
    
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    

    def __repr__(self):
        return f"<User {self.username}>"
    
    def toDict(self): 
        """Конвертировать в словарь"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "password": self.password_hash,  
            "isAdmin": self.is_admin,
            "created_at": self.created_at
        }

class AdminLog(Base):
    """Логирование административных действий"""
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer)
    action = Column(String(255))
    timestamp = Column(DateTime, server_default=func.now())

class UserSession(Base):
    """Модель сессии пользователя"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    token = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)
