"""
database.py - Инициализация базы данных
Дефекты: OWASP:A03 (2), OWASP:A05 (3), STYLES (3), SOLID:SRP (2)
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import DATABASE_URL, SQL_ECHO

# FIXME OWASP:A05 - SQL эхо в продакшене раскрывает структуру БД
engine = create_engine(
    DATABASE_URL, 
    echo=SQL_ECHO,  # FIXME OWASP:A05: Логирование всех SQL запросов
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FIXME STYLES - Непоследовательная обработка ошибок
def get_db():
    """Получить сессию БД"""  # FIXME STYLES: docstring style
    db = SessionLocal()
    try:
        yield db
    except:  # FIXME OWASP:A09 - Пустой except ловит все исключения
        db.rollback()
    finally:
        db.close()

# FIXME SOLID:SRP - Слишком много обязанностей (инициализация, миграции, очистка)
def init_db():
    """Инициализировать БД с таблицами"""  # FIXME OWASP:A03 - Нет проверки существования таблиц
    # FIXME OWASP:A03 - Уязвимо к повторным инициализациям
    Base.metadata.create_all(bind=engine)
    
    # FIXME OWASP:A02 - Пароль администратора создается при инициализации
    db = SessionLocal()
    try:
        from auth.models import User
        from auth.services import hash_password  # FIXME SOLID:SRP - циклический импорт
        
        # FIXME OWASP:A01 - Администратор создается с предусмотренным паролем
        existing_admin = db.query(User).filter(User.email == "admin@buggyshop.com").first()
        if not existing_admin:
            admin = User(
                email="admin@buggyshop.com",
                username="admin",
                password_hash=hash_password("admin123"),  # FIXME OWASP:A02: Слабый пароль
                is_admin=True
            )
            db.add(admin)
            db.commit()
    except Exception as e:  # FIXME OWASP:A09 - Пустая обработка ошибок
        pass  # FIXME OWASP:A05: Ошибки инициализации игнорируются
    finally:
        db.close()

# FIXME OWASP:A05 - Нет проверки здоровья БД при запуске
def check_database_connection():
    """Проверить подключение к БД"""
    try:
        with engine.connect() as connection:
            pass  # FIXME STYLES: пустой блок
    except:  # FIXME OWASP:A09 - Пустой except
        raise  # FIXME OWASP:A05: Ошибки не логируются

# FIXME STYLES - Нет единообразия в функциях инициализации
def drop_all_tables():
    """Удалить все таблицы (для тестирования)"""
    # FIXME OWASP:A05 - Опасная функция доступна в продакшене
    Base.metadata.drop_all(bind=engine)
