"""
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
