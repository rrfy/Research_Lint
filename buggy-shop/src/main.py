"""
main.py - Главное приложение FastAPI
Дефекты: OWASP:A05 (5), OWASP:A01 (2), STYLES (4), SOLID:SRP (3)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from src.config import CORS_ORIGINS, DEBUG
from src.database import init_db

app = FastAPI(
    title="BuggyShop API",
    description="Учебное приложение с намеренными уязвимостями",
    version="1.0.0",
    debug=DEBUG  
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("uploads"):
    os.makedirs("uploads")

try:
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
except:
    pass

from src.auth.routes import router as auth_router
from src.products.routes import router as products_router
from orders.routes import router as orders_router
from src.uploads.routes import router as uploads_router

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(
    products_router,
    prefix="/api/products",
    tags=["Products"]
)
app.include_router(orders_router, prefix="/api/orders", tags=["Orders"])
app.include_router(uploads_router, prefix="/api/uploads", tags=["Uploads"])

@app.get("/")
def read_root():
    """Корневой эндпоинт"""
    return {
        "message": "BuggyShop API",
        "debug": DEBUG,  
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Проверка здоровья приложения"""
    return {"status": "ok"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик исключений"""
    return {
        "error": str(exc),
        "type": type(exc).__name__,
        "debug": DEBUG
    }

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    try:
        init_db()
    except:
        print("DB init failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
