"""
auth/routes.py - REST API маршруты для аутентификации
Дефекты: OWASP:A01 (5), OWASP:A07 (4), STYLES (5), SOLID:SRP (3)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from src.auth.models import User
from src.auth.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from src.auth.services import (
    register_user, 
    authenticate_user,
    create_access_token,
    get_user,
    update_user,
    delete_user,
    make_admin
)
from src.auth.dependencies import get_current_user, get_admin_user
from src.database import get_db
from src.config import JWT_EXPIRATION_HOURS

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
