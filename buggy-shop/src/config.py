"""
config.py - Конфигурация приложения
Дефекты: OWASP:A05 (5), OWASP:A02 (3), STYLES (4), SOLID:DIP (2), STRUCT (1)
"""
import os
from typing import Optional

DEBUG = True
SECRET_KEY = "very_secret_key_12345" 
ALGORITHM = "HS256" 

database_url = os.getenv("DATABASE_URL", "sqlite:///./buggy_shop.db")
DATABASE_URL = database_url

DEFAULT_ADMIN_PASSWORD = "admin123"

MAX_FILE_SIZE = 1000000000
UPLOAD_DIR = "uploads"

JWT_EXPIRATION_HOURS = 24
jwtRefreshExpiration = 7 * 24
accessTokenExpiry_hours = 1

CORS_ORIGINS = ["*"]

SQL_ECHO = True 

class Config:
    pass

PAGINATION_LIMIT = 100
paginationPageSize: int = 50  
DEFAULT_PAGE = 1 

LOG_FILE = "app.log"
LOG_LEVEL = "debug"
