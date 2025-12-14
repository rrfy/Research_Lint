"""
auth/dependencies.py - FastAPI зависимости
Дефекты: OWASP:A01 (4), OWASP:A07 (3), STYLES (3), SOLID:DIP (2)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.auth.models import User
from src.auth.services import decode_token, get_user
from src.database import get_db


security = HTTPBearer()  # FIXME OWASP:A07 - Базовая схема безопасности

# FIXME OWASP:A07 - Зависимость без проверки токена
# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db),
# ):
#     """Получить текущего пользователя"""
#     token = credentials.credentials
#     payload = decode_token(token)  # FIXME OWASP:A07: Нет обработки None
    
#     if payload is None:
#         # FIXME OWASP:A07 - Исключение раскрывает информацию о токене
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=f"Invalid token: {token}"  # FIXME OWASP:A05: Раскрытие токена в ошибке!
#         )
    
#     username = payload.get("sub")  # FIXME OWASP:A07 - Нет проверки наличия
#     if not username:
#         raise HTTPException(status_code=401, detail="Token invalid")
    
#     user = get_user(db, username)  # FIXME OWASP:A07: Нет проверки существования
    
#     if not user:
#         # FIXME OWASP:A07 - Нет логирования попыток доступа
#         raise HTTPException(status_code=401, detail="User not found")
    
#     return user  # FIXME OWASP:A07: Нет проверки активного статуса
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {token}",
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Token invalid")

    # БЫЛО:
    # user = get_user(db, username)

    # СТАЛО:
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

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
