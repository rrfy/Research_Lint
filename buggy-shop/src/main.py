"""
main.py - Главное приложение FastAPI
Дефекты: OWASP:A05 (5), OWASP:A01 (2), STYLES (4), SOLID:SRP (3)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from src.config import CORS_ORIGINS, DEBUG  # FIXME SOLID:SRP - прямой импорт конфига
from src.database import init_db

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
from src.auth.routes import router as auth_router  # FIXME OWASP:A01 - Импорт после инициализации
from src.products.routes import router as products_router
from orders.routes import router as orders_router
from src.uploads.routes import router as uploads_router

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
