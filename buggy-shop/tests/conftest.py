# tests/conftest.py
import os
import sys
from pathlib import Path
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# --- sys.path ДО импортов приложения ---
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT))

# --- алиасы модулей ---
import importlib
for pkg in ("auth", "orders", "products", "uploads"):
    if pkg not in sys.modules:
        sys.modules[pkg] = importlib.import_module(f"src.{pkg}")

from src.main import app  # noqa: E402
from src.database import Base, get_db  # noqa: E402

# SQLite в памяти для полной изоляции
TEST_DATABASE_URL = "sqlite://"


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    os.environ["ENV"] = "test"
    yield
    if os.path.exists("uploads"):
        import shutil
        shutil.rmtree("uploads", ignore_errors=True)


@pytest.fixture(scope="session")
def engine():
    """Движок БД для всех тестов (в памяти)"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    """Сессия БД с транзакционной изоляцией (откат после каждого теста)"""
    connection = engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(bind=connection, autocommit=False, autoflush=False, expire_on_commit=False)
    session = TestingSessionLocal()

    # nested transaction (SAVEPOINT) для имитации commit внутри теста
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient с переопределённой БД и отключенным startup"""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # отключаем startup_event (init_db)
    original_startup = list(app.router.on_startup)
    app.router.on_startup.clear()

    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.router.on_startup[:] = original_startup
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(client):
    """Уникальный тестовый пользователь (каждый тест)"""
    u = uuid.uuid4().hex[:8]
    user_data = {
        "email": f"test_{u}@example.com",
        "username": f"testuser_{u}",
        "password": "TestPass123!",
    }
    r = client.post("/api/auth/register", json=user_data)
    assert r.status_code in (200, 201), f"Register failed: {r.text}"
    return user_data


@pytest.fixture(scope="function")
def auth_token(client, test_user):
    """JWT токен для test_user"""
    login_data = {"username": test_user["username"], "password": test_user["password"]}
    r = client.post("/api/auth/login", json=login_data)
    assert r.status_code == 200, f"Login failed: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """Заголовки авторизации для test_user"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def test_admin(client, db_session):
    """Уникальный админ (каждый тест)"""
    from src.auth.models import User
    from src.auth.services import hash_password

    u = uuid.uuid4().hex[:8]
    admin = User(
        email=f"admin_{u}@example.com",
        username=f"admin_{u}",
        password_hash=hash_password("AdminPass123!"),
        is_admin=True,
    )
    db_session.add(admin)
    db_session.commit()

    r = client.post("/api/auth/login", json={"username": admin.username, "password": "AdminPass123!"})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    token = r.json()["access_token"]
    return {"headers": {"Authorization": f"Bearer {token}"}, "user": admin}
