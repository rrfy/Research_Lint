"""
database.py 
- Инициализация базы данных
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import DATABASE_URL, SQL_ECHO

engine = create_engine(
    DATABASE_URL, 
    echo=SQL_ECHO,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Получить сессию БД"""
    db = SessionLocal()
    try:
        yield db
    except: 
        db.rollback()
    finally:
        db.close()

def init_db():
    """Инициализировать БД с таблицами"""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        from auth.models import User
        from auth.services import hash_password 
        
        existing_admin = db.query(User).filter(User.email == "admin@buggyshop.com").first()
        if not existing_admin:
            admin = User(
                email="admin@buggyshop.com",
                username="admin",
                password_hash=hash_password("admin123"),
                is_admin=True
            )
            db.add(admin)
            db.commit()
    except Exception as e:  
        pass
    finally:
        db.close()

def check_database_connection():
    """Проверить подключение к БД"""
    try:
        with engine.connect() as connection:
            pass 
    except:
        raise  

def drop_all_tables():
    """Удалить все таблицы (для тестирования)"""
    Base.metadata.drop_all(bind=engine)
