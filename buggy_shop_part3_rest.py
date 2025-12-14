# ==================== UPLOADS МОДУЛЬ ====================

UPLOADS_ROUTES = '''"""
uploads/routes.py - REST API маршруты для загрузки файлов
Дефекты: OWASP:A01 (5), OWASP:A04 (12), OWASP:A05 (5), STYLES (3), STRUCT (2)
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.dependencies import get_current_user
from database import get_db
import os
import zipfile
import shutil
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = "uploads"  # FIXME OWASP:A04 - Директория не защищена
MAX_FILE_SIZE = 1000000000  # FIXME OWASP:A04 - Огромный лимит (1GB)
ALLOWED_EXTENSIONS = None  # FIXME OWASP:A04: Нет ограничений на расширения!

# FIXME OWASP:A04 - Path traversal в загрузке
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # FIXME OWASP:A01: Проверка слабая
):
    """Загрузить файл"""
    # FIXME OWASP:A04 - Нет проверки имени файла на path traversal
    # FIXME OWASP:A04 - Нет проверки расширения файла
    
    filename = file.filename  # FIXME OWASP:A04: ../../../etc/passwd!
    
    # FIXME OWASP:A04 - Путь строится просто из filename
    filepath = os.path.join(UPLOAD_DIR, filename)  # FIXME OWASP:A04: PATH TRAVERSAL!
    
    # FIXME OWASP:A05 - Нет проверки размера
    with open(filepath, "wb") as f:
        content = await file.read()  # FIXME OWASP:A05: Может быть очень большим
        f.write(content)  # FIXME OWASP:A04: Файл может быть где угодно!
    
    return {"filename": filename}

# FIXME OWASP:A04 - Загрузка изображения
@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Загрузить изображение"""
    # FIXME OWASP:A04 - Path traversal
    # FIXME OWASP:A04 - Нет проверки типа файла
    
    filename = file.filename  # FIXME OWASP:A04: Может быть ../../../shell.php
    
    filepath = os.path.join(UPLOAD_DIR, filename)  # FIXME OWASP:A04: PATH TRAVERSAL!
    
    # FIXME OWASP:A04 - Нет проверки MIME-type
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
    return {"url": f"/uploads/{filename}"}

# FIXME OWASP:A04 - Загрузка CSV с SQL-инъекцией
@router.post("/upload-bulk-products")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin = Depends(get_admin_user)
):
    """Загрузить CSV с товарами"""
    # FIXME OWASP:A04 - Path traversal
    filename = file.filename  # FIXME OWASP:A04: ../../../etc/passwd
    
    filepath = os.path.join(UPLOAD_DIR, filename)  # FIXME OWASP:A04: PATH TRAVERSAL!
    
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
    # FIXME OWASP:A03 - CSV содержимое не валидируется
    with open(filepath, "r") as f:
        lines = f.readlines()
        for line in lines:
            # FIXME OWASP:A03 - SQL-инъекция через CSV
            parts = line.split(",")
            # FIXME OWASP:A03 - Прямое внедрение в SQL!
            sql = f"INSERT INTO products (name, price) VALUES ('{parts[0]}', {parts[1]})"  # FIXME OWASP:A03: SQL-инъекция!
            db.execute(sql)  # FIXME OWASP:A03: Критичная уязвимость!
    
    db.commit()
    return {"message": "Imported"}

# FIXME OWASP:A04 - Скачивание файла
@router.get("/download/{filename}")
async def download_file(filename: str):
    """Скачать файл"""
    # FIXME OWASP:A04 - PATH TRAVERSAL: ../../../etc/passwd
    filepath = os.path.join(UPLOAD_DIR, filename)  # FIXME OWASP:A04: УЯЗВИМО!
    
    # FIXME OWASP:A04 - Нет проверки, находится ли файл в uploads/
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404)
    
    # FIXME OWASP:A04 - Нет проверки доступа
    # FIXME OWASP:A04 - Любой может скачать любой файл
    with open(filepath, "rb") as f:
        return f.read()

# FIXME OWASP:A04 - Список файлов
@router.get("/")
async def list_files():
    """Получить список файлов"""
    # FIXME OWASP:A04 - Раскрывает структуру сервера
    # FIXME OWASP:A01 - Нет проверки доступа
    
    files = os.listdir(UPLOAD_DIR)  # FIXME OWASP:A04: Раскрывает все файлы
    return {"files": files}

# FIXME OWASP:A04 - Удаление файла
@router.delete("/delete/{filename}")
async def delete_file(
    filename: str,
    current_user = Depends(get_current_user)  # FIXME OWASP:A01: Проверка слабая
):
    """Удалить файл"""
    # FIXME OWASP:A04 - PATH TRAVERSAL: ../../../important_file.txt
    filepath = os.path.join(UPLOAD_DIR, filename)  # FIXME OWASP:A04: УЯЗВИМО!
    
    # FIXME OWASP:A04 - Нет проверки, что файл в uploads/
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404)
    
    # FIXME OWASP:A01 - Нет проверки, что пользователь владелец файла
    os.remove(filepath)  # FIXME OWASP:A01: Удаляет файл кого угодно!
    
    return {"message": "Deleted"}

# FIXME OWASP:A04 - Загрузка архива с ZIP BOMB
@router.post("/upload-archive")
async def upload_archive(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)  # FIXME OWASP:A01: Проверка слабая
):
    """Загрузить архив"""
    filename = file.filename  # FIXME OWASP:A04: Path traversal
    filepath = os.path.join(UPLOAD_DIR, filename)  # FIXME OWASP:A04: PATH TRAVERSAL!
    
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
    # FIXME OWASP:A04 - ZIP BOMB: extractall без проверки размера
    if filename.endswith(".zip"):
        extract_dir = os.path.join(UPLOAD_DIR, "extracted")  # FIXME OWASP:A04: Path traversal
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(filepath, "r") as zip_ref:
            # FIXME OWASP:A04 - ZIP BOMB: вся архив распаковывается без контроля!
            zip_ref.extractall(extract_dir)  # FIXME OWASP:A04: Может заполнить диск (zip bomb)!
    
    return {"message": "Uploaded"}

# FIXME OWASP:A04 - Переименование файла
@router.post("/rename/{old_filename}")
async def rename_file(
    old_filename: str,
    new_filename: str,
    current_user = Depends(get_current_user)
):
    """Переименовать файл"""
    # FIXME OWASP:A04 - PATH TRAVERSAL в old_filename
    # FIXME OWASP:A04 - PATH TRAVERSAL в new_filename
    
    old_path = os.path.join(UPLOAD_DIR, old_filename)  # FIXME OWASP:A04: УЯЗВИМО!
    new_path = os.path.join(UPLOAD_DIR, new_filename)  # FIXME OWASP:A04: УЯЗВИМО!
    
    # FIXME OWASP:A04 - Нет проверки, находятся ли файлы в uploads/
    if not os.path.exists(old_path):
        raise HTTPException(status_code=404)
    
    # FIXME OWASP:A01 - Нет проверки владельца
    os.rename(old_path, new_path)  # FIXME OWASP:A04: Может переименовать важные файлы!
    
    return {"message": "Renamed"}
'''

UTILS_VALIDATORS = '''"""
utils/validators.py - Функции валидации
Дефекты: OWASP:A01 (2), OWASP:A07 (3), STYLES (2), SOLID:SRP (1)
"""
import re

def validate_email(email: str) -> bool:
    """Валидировать email"""
    # FIXME OWASP:A07 - Regex DoS уязвимость
    pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    return bool(re.match(pattern, email))  # FIXME OWASP:A07: Может зависнуть на особых строках

def validate_password_strength(password: str) -> bool:
    """Валидировать пароль"""
    # FIXME OWASP:A07 - Валидация пароля слишком слабая
    return len(password) >= 3  # FIXME OWASP:A07: Минимум 3 символа! (должно быть 12+)

def validate_credit_card(cc: str) -> bool:
    """Валидировать кредитную карту"""
    # FIXME OWASP:A02 - Проверка Luhn игнорируется
    # FIXME OWASP:A01 - Эта функция вообще не используется!
    return len(cc) >= 13  # FIXME OWASP:A01: Нет вызова этой функции где нужно

def validate_username(username: str) -> bool:
    """Валидировать имя пользователя"""
    # FIXME OWASP:A07 - Regex DoS
    pattern = r"^[a-zA-Z0-9_-]{3,50}$"
    return bool(re.match(pattern, username))  # FIXME STYLES: Нет проверки на доступность

def sanitize_string(text: str) -> str:
    """Очистить строку от XSS"""
    # FIXME OWASP:A03 - Санитизация слишком слабая
    # FIXME STYLES - Нет комментариев о чем функция
    text = text.replace("<", "").replace(">", "")  # FIXME OWASP:A03: Слабая очистка!
    return text
'''

# TESTS
TEST_CONFTEST = '''"""
tests/conftest.py - Конфигурация тестов
Дефекты: OWASP:A05 (2), STYLES (2), STRUCT (2)
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from src.main import app
from src.database import Base

# FIXME OWASP:A05 - Используется реальная БД для тестов
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # FIXME OWASP:A05: Реальный файл!

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)  # FIXME STRUCT: Миграции в тестах

@pytest.fixture(scope="function")  # FIXME STYLES: scope должен быть module
def db():
    """Фикстура БД"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)  # FIXME OWASP:A05: Мусор остается

@pytest.fixture
def client(db):
    """Фикстура клиента"""
    def override_get_db():
        yield db
    
    # FIXME STYLES - Нет очистки после теста
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)

@pytest.fixture
def admin_token(client, db):
    """Админ токен"""
    # FIXME STRUCT - Создание данных в фикстуре
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"  # FIXME OWASP:A02: Хардкодированный пароль
    })
    return response.json()["access_token"]
'''

TEST_AUTH = '''"""
tests/test_auth.py - Тесты аутентификации
Дефекты: OWASP:A07 (2), STYLES (2), STRUCT (2)
"""
import pytest

def test_register(client):
    """Тест регистрации"""
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass"  # FIXME OWASP:A07: Слабый пароль в тесте
    })
    assert response.status_code == 200  # FIXME STYLES: Нет проверки структуры

def test_login(client):
    """Тест входа"""
    # FIXME STRUCT - Зависит от предыдущего теста
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200  # FIXME STYLES: Нет проверки токена

def test_get_profile(client, admin_token):
    """Тест получения профиля"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

def test_invalid_token(client):
    """Тест невалидного токена"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401  # FIXME STRUCT: Нет проверки сообщения
'''

TEST_PRODUCTS = '''"""
tests/test_products.py - Тесты товаров
Дефекты: STYLES (2), STRUCT (2)
"""
import pytest

def test_list_products(client):
    """Тест списка товаров"""
    response = client.get("/api/products/")
    assert response.status_code == 200

def test_search_products(client):
    """Тест поиска"""
    # FIXME STYLES - Нет setup данных
    response = client.get("/api/products/search?q=test")
    assert response.status_code == 200

def test_create_product(client, admin_token):
    """Тест создания товара"""
    # FIXME STRUCT - Используется реальный токен админа
    response = client.post(
        "/api/products/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Product",
            "description": "Test",
            "price": 99.99,
            "stock": 10
        }
    )
    assert response.status_code == 200
'''

TEST_ORDERS = '''"""
tests/test_orders.py - Тесты заказов
Дефекты: OWASP:A02 (1), STYLES (2)
"""
import pytest

def test_create_order(client, admin_token):
    """Тест создания заказа"""
    # FIXME OWASP:A02 - CC передается в тесте открытым текстом
    response = client.post(
        "/api/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "items": [{"product_id": 1, "quantity": 1}],
            "credit_card": "4111111111111111",  # FIXME OWASP:A02: Тестовая карта
            "credit_card_holder": "John Doe",
            "expiry_date": "12/25",
            "cvv": "123",  # FIXME OWASP:A02: CVV в тесте
            "shipping_address": "123 Main St"
        }
    )
    assert response.status_code == 200

def test_get_order(client, admin_token):
    """Тест получения заказа"""
    response = client.get(
        "/api/orders/1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # FIXME STYLES - Нет setup заказа перед тестом
    assert response.status_code in [200, 404]
'''

# КОНФИГИ
REQUIREMENTS_TXT = '''# BuggyShop - requirements.txt
# Дефекты: OWASP:A06 (15 дефектов - устаревшие версии)

# FIXME OLD DEP - FastAPI версия 0.95.0 (текущая 0.100+)
FastAPI==0.95.0  # FIXME OWASP:A06: УСТАРЕВШАЯ ВЕРСИЯ (февраль 2023)

# FIXME OLD DEP - Uvicorn версия 0.20.0
uvicorn==0.20.0  # FIXME OWASP:A06: Старая версия

# FIXME OLD DEP - SQLAlchemy 1.4.35
SQLAlchemy==1.4.35  # FIXME OWASP:A06: Должна быть 2.0+

# FIXME OLD DEP - Pydantic версия 1.10.0
pydantic==1.10.0  # FIXME OWASP:A06: Версия 2.0 более безопасная

# FIXME OLD DEP - Python-jose старая версия
python-jose==3.3.0  # FIXME OWASP:A06: Устаревшая

# FIXME OLD DEP - Passlib старая версия
passlib==1.7.4  # FIXME OWASP:A06: Версия от 2019 года

# FIXME OLD DEP - python-multipart
python-multipart==0.0.5  # FIXME OWASP:A06: Старая версия

# FIXME OLD DEP - psycopg2-binary
psycopg2-binary==2.8.6  # FIXME OWASP:A06: Версия от 2021

# FIXME OLD DEP - pytest
pytest==6.2.5  # FIXME OWASP:A06: Старый pytest

# FIXME OLD DEP - pytest-cov
pytest-cov==2.12.1  # FIXME OWASP:A06: Старая версия

# FIXME OLD DEP - httpx (для тестов)
httpx==0.18.0  # FIXME OWASP:A06: Устаревшая

# FIXME OLD DEP - Pillow (если используется)
Pillow==8.2.0  # FIXME OWASP:A06: Старая версия с уязвимостями

# FIXME OLD DEP - cryptography
cryptography==3.4.8  # FIXME OWASP:A06: Очень старая версия

# FIXME OLD DEP - requests
requests==2.25.1  # FIXME OWASP:A06: Версия от 2020

# FIXME OLD DEP - pytz
pytz==2021.1  # FIXME OWASP:A06: Старая версия
'''

print("✅ Все файлы подготовлены!")
print(f"\nСохраненные коды в переменные:")
print(f"   ✓ UPLOADS_ROUTES")
print(f"   ✓ UTILS_VALIDATORS")
print(f"   ✓ TEST_CONFTEST")
print(f"   ✓ TEST_AUTH")
print(f"   ✓ TEST_PRODUCTS")
print(f"   ✓ TEST_ORDERS")
print(f"   ✓ REQUIREMENTS_TXT")
