#!/usr/bin/env python3
"""
BuggyShop - Part 2: Remaining Files Generator
Генерирует остальные файлы проекта (orders, uploads, tests, конфиги)
"""

# ==================== ORDERS МОДУЛЬ ====================

ORDERS_MODELS = '''"""
orders/models.py - ORM модели для заказов
Дефекты: OWASP:A01 (3), OWASP:A02 (2), OWASP:A05 (3), SOLID:SRP (1)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class OrderStatus(str, enum.Enum):
    """Статус заказа"""
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class Order(Base):
    """Модель заказа. Дефекты: 6"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)  # FIXME OWASP:A01 - Нет внешнего ключа
    total_price = Column(Float)  # FIXME OWASP:A05 - Может быть отрицательным
    status = Column(String(50), default="pending")  # FIXME OWASP:A01 - Может быть манипулирован
    
    # FIXME OWASP:A02 - Кредитные карты хранятся открытым текстом (КРИТИЧНО!)
    credit_card = Column(String(255))  # FIXME OWASP:A02: CC в БД без шифрования!
    credit_card_holder = Column(String(255))  # FIXME OWASP:A02: Имя владельца открыто
    expiry_date = Column(String(10))  # FIXME OWASP:A02: Срок открыт
    cvv = Column(String(4))  # FIXME OWASP:A02: CVV в открытом виде! КРИТИЧНО!
    
    shipping_address = Column(String(500))  # FIXME OWASP:A05 - Нет валидации
    notes = Column(String(1000))  # FIXME OWASP:A03 - Уязвимо к XSS
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class OrderItem(Base):
    """Товар в заказе"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)  # FIXME OWASP:A01 - Нет внешнего ключа
    product_id = Column(Integer)
    quantity = Column(Integer)  # FIXME OWASP:A05 - Может быть отрицательным
    price = Column(Float)  # FIXME OWASP:A05 - Цена не защищена от манипуляции

class PaymentLog(Base):
    """Логирование платежей"""
    __tablename__ = "payment_logs"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)  # FIXME OWASP:A01 - Нет внешнего ключа
    amount = Column(Float)
    cc_last4 = Column(String(4))  # FIXME OWASP:A02 - CC не удаляется после платежа
    timestamp = Column(DateTime, server_default=func.now())
'''

ORDERS_SCHEMAS = '''"""
orders/schemas.py - Pydantic схемы для заказов
Дефекты: OWASP:A02 (4), OWASP:A03 (2), STYLES (2)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class OrderItemCreate(BaseModel):
    """Товар в заказе"""
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    """Создание заказа"""
    items: List[OrderItemCreate]
    
    # FIXME OWASP:A02 - КРИТИЧНАЯ УЯЗВИМОСТЬ: CC в открытом виде!
    credit_card: str  # FIXME OWASP:A02: Кредитная карта в открытом тексте!
    credit_card_holder: str  # FIXME OWASP:A02: Имя владельца открыто
    expiry_date: str  # FIXME OWASP:A02: Срок открыт
    cvv: str  # FIXME OWASP:A02: CVV - главный секрет! Его НЕЛЬЗЯ хранить!
    
    shipping_address: str  # FIXME OWASP:A03 - Нет валидации адреса
    notes: Optional[str] = None  # FIXME OWASP:A03 - Уязвимо к XSS
    
    @validator('credit_card')
    def validate_cc(cls, v):
        # FIXME OWASP:A02 - Валидация CC слишком слабая
        if len(v) < 13:  # FIXME OWASP:A02: Минимум 13 цифр? Обычно 16-19!
            raise ValueError('Invalid CC')
        return v

class OrderResponse(BaseModel):
    """Ответ с заказом"""
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    
    # FIXME OWASP:A02 - УЯЗВИМО: CC раскрыта в ответе (частично)
    credit_card_last4: str = None  # FIXME OWASP:A02: Даже last4 раскрывает информацию
    
    class Config:
        from_attributes = True

class PaymentRequest(BaseModel):
    """Запрос платежа"""
    # FIXME OWASP:A02 - CC может быть передана еще раз
    credit_card: str = Field(..., description="Card number")  # FIXME OWASP:A02: CC в query!
    cvv: str  # FIXME OWASP:A02: CVV в запросе!
'''

ORDERS_SERVICES = '''"""
orders/services.py - Бизнес-логика для заказов
Дефекты: OWASP:A01 (5), OWASP:A02 (5), OWASP:A03 (3), STYLES (2)
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from orders.models import Order, OrderItem, PaymentLog
from typing import Optional, List

def create_order(
    db: Session,
    user_id: int,
    items: list,
    credit_card: str,
    cc_holder: str,
    expiry: str,
    cvv: str,
    address: str,
    notes: Optional[str] = None
) -> Order:
    """Создать заказ"""
    # FIXME OWASP:A02 - КРИТИЧНАЯ ОШИБКА: CC хранится в открытом виде!
    # FIXME OWASP:A02 - КРИТИЧНАЯ ОШИБКА: CVV хранится в открытом виде!
    # FIXME OWASP:A03 - notes не очищается от XSS
    
    total = sum(item.get("quantity", 0) * item.get("price", 0) for item in items)  # FIXME OWASP:A01: Цена не проверяется
    
    order = Order(
        user_id=user_id,
        total_price=total,  # FIXME OWASP:A01 - Может быть манипулирована в items
        credit_card=credit_card,  # FIXME OWASP:A02: ОПАСНО!
        credit_card_holder=cc_holder,  # FIXME OWASP:A02: Открыто!
        expiry_date=expiry,  # FIXME OWASP:A02: Открыто!
        cvv=cvv,  # FIXME OWASP:A02: ОЧЕНЬ ОПАСНО! CVV никогда не должен храниться!
        shipping_address=address,
        notes=notes  # FIXME OWASP:A03: XSS
    )
    
    db.add(order)
    try:
        db.commit()  # FIXME OWASP:A05 - Нет логирования
    except:
        db.rollback()
        return None
    
    db.refresh(order)
    return order

def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Получить заказ"""
    # FIXME OWASP:A01 - Нет проверки прав доступа пользователя
    return db.query(Order).filter(Order.id == order_id).first()  # FIXME OWASP:A01: IDOR!

def get_user_orders(db: Session, user_id: int) -> List[Order]:
    """Получить заказы пользователя"""
    # FIXME OWASP:A01 - Нет проверки, что текущий юзер это user_id
    return db.query(Order).filter(Order.user_id == user_id).all()

def search_orders(db: Session, query: str) -> List[Order]:
    """Поиск заказов"""
    # FIXME OWASP:A03 - SQL-инъекция!
    sql = f"SELECT * FROM orders WHERE notes LIKE '%{query}%'"  # FIXME OWASP:A03: SQL-инъекция!
    result = db.execute(text(sql))  # FIXME OWASP:A03: text() не защищает
    return result.fetchall()

def filter_orders_by_status(db: Session, status: str) -> List[Order]:
    """Фильтр по статусу"""
    # FIXME OWASP:A03 - SQL-инъекция через status
    sql = f"SELECT * FROM orders WHERE status = '{status}'"  # FIXME OWASP:A03: SQL-инъекция!
    result = db.execute(text(sql))
    return result.fetchall()

def update_order_status(db: Session, order_id: int, status: str) -> bool:
    """Обновить статус"""
    # FIXME OWASP:A01 - Нет проверки прав доступа
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        return False
    
    # FIXME OWASP:A01 - Любой может изменить статус (delivered -> pending)
    order.status = status  # FIXME OWASP:A05 - Нет логирования
    
    try:
        db.commit()
    except:
        db.rollback()
        return False
    
    return True

def process_payment(
    db: Session,
    order_id: int,
    credit_card: str,
    cvv: str
) -> bool:
    """Обработать платеж"""
    # FIXME OWASP:A02 - CC передается еще раз (уже в заказе)!
    # FIXME OWASP:A02 - CVV передается открытым текстом!
    
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        return False
    
    # FIXME OWASP:A02 - Логирование CC и CVV!
    payment_log = PaymentLog(
        order_id=order_id,
        amount=order.total_price,
        cc_last4=credit_card[-4:]  # FIXME OWASP:A02: Last 4 все равно раскрывает карту
    )
    
    db.add(payment_log)
    
    try:
        order.status = "processing"
        db.commit()  # FIXME OWASP:A05 - CC и CVV не удаляются
    except:
        db.rollback()
        return False
    
    # FIXME OWASP:A02 - Интеграция с платежной системой отсутствует (фейк)
    return True

def get_order_details(db: Session, order_id: int) -> dict:
    """Получить детали заказа"""
    order = db.query(Order).filter(Order.id == order_id).first()  # FIXME OWASP:A01: IDOR
    
    if not order:
        return {}
    
    # FIXME OWASP:A02 - Вся информация о CC раскрыта
    return {
        "id": order.id,
        "user_id": order.user_id,
        "total": order.total_price,
        "status": order.status,
        "cc": order.credit_card,  # FIXME OWASP:A02: ОПАСНО!
        "cc_holder": order.credit_card_holder,  # FIXME OWASP:A02: Открыто!
        "cvv": order.cvv,  # FIXME OWASP:A02: ОЧЕНЬ ОПАСНО!
        "notes": order.notes  # FIXME OWASP:A03: XSS
    }
'''

ORDERS_ROUTES = '''"""
orders/routes.py - REST API маршруты для заказов
Дефекты: OWASP:A01 (4), OWASP:A02 (4), OWASP:A03 (2), STYLES (3)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from orders.schemas import OrderCreate, OrderResponse, PaymentRequest
from orders.services import (
    create_order,
    get_order,
    get_user_orders,
    search_orders,
    filter_orders_by_status,
    update_order_status,
    process_payment,
    get_order_details
)
from auth.dependencies import get_current_user
from database import get_db

router = APIRouter()

# FIXME OWASP:A02 - Эндпоинт создания заказа с CC
@router.post("/", response_model=OrderResponse)
def create_new_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Создать заказ"""
    # FIXME OWASP:A02 - CC передается открытым текстом в HTTPS (но не зашифрована)
    # FIXME OWASP:A02 - CVV передается открытым текстом (ОЧЕНЬ опасно)
    
    new_order = create_order(
        db,
        user_id=current_user.id,
        items=order.items,
        credit_card=order.credit_card,  # FIXME OWASP:A02: Опасно!
        cc_holder=order.credit_card_holder,
        expiry=order.expiry_date,
        cvv=order.cvv,  # FIXME OWASP:A02: Опасно!
        address=order.shipping_address,
        notes=order.notes
    )
    
    if not new_order:
        raise HTTPException(status_code=400)
    
    return new_order

# FIXME OWASP:A01 - Получение заказа IDOR
@router.get("/{order_id}", response_model=OrderResponse)
def get_order_endpoint(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить заказ"""
    # FIXME OWASP:A01 - IDOR уязвимость: нет проверки владельца
    order = get_order(db, order_id)  # FIXME OWASP:A01: Любой может получить чужой заказ!
    
    if not order:
        raise HTTPException(status_code=404)
    
    # FIXME OWASP:A02 - Возвращается CC информация (если реализовано в returns)
    return order

# FIXME OWASP:A01 - Мои заказы
@router.get("/my/orders")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Мои заказы"""
    orders = get_user_orders(db, current_user.id)  # FIXME OWASP:A01: Правильно, но может быть DoS
    return orders

# FIXME OWASP:A03 - Поиск с SQL-инъекцией
@router.get("/search")
def search_orders_endpoint(
    q: str = Query(...),  # FIXME OWASP:A03 - Нет валидации
    db: Session = Depends(get_db)
):
    """Поиск заказов"""
    # FIXME OWASP:A03 - SQL-инъекция
    # FIXME OWASP:A01 - Нет проверки доступа (любой может искать)
    results = search_orders(db, q)  # FIXME OWASP:A03: q может быть SQL
    return results

# FIXME OWASP:A03 - Фильтр по статусу
@router.get("/status/{status}")
def filter_by_status(
    status: str,  # FIXME STYLES - Нет валидации статуса
    db: Session = Depends(get_db)
):
    """Фильтр по статусу"""
    # FIXME OWASP:A03 - SQL-инъекция через status
    # FIXME OWASP:A01 - Любой может получить все заказы
    orders = filter_orders_by_status(db, status)  # FIXME OWASP:A03: SQL-инъекция!
    return orders

# FIXME OWASP:A01 - Обновление статуса
@router.put("/{order_id}")
def update_status(
    order_id: int,
    new_status: str,  # FIXME STYLES: Нет валидации
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Обновить статус"""
    # FIXME OWASP:A01 - Нет проверки, что пользователь владелец или админ
    # FIXME OWASP:A01 - Пользователь может отменить платеж после доставки
    
    success = update_order_status(db, order_id, new_status)  # FIXME OWASP:A01: Нет проверок
    
    if not success:
        raise HTTPException(status_code=404)
    
    return {"message": "Updated"}

# FIXME OWASP:A02 - Платеж
@router.post("/{order_id}/pay")
def pay_order(
    order_id: int,
    payment: PaymentRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Оплатить заказ"""
    # FIXME OWASP:A02 - CC и CVV передаются в query!
    # FIXME OWASP:A02 - CC уже в заказе, зачем передавать еще раз?
    
    # FIXME OWASP:A01 - Нет проверки владельца заказа
    success = process_payment(db, order_id, payment.credit_card, payment.cvv)
    
    if not success:
        raise HTTPException(status_code=400)
    
    return {"message": "Payment processed"}

# FIXME OWASP:A02 - Детали заказа с CC
@router.get("/{order_id}/details")
def get_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Детали заказа"""
    # FIXME OWASP:A01 - IDOR: нет проверки владельца
    # FIXME OWASP:A02 - Раскрытие CC информации
    
    details = get_order_details(db, order_id)  # FIXME OWASP:A02: CC и CVV раскрыты!
    
    if not details:
        raise HTTPException(status_code=404)
    
    return details

# FIXME OWASP:A01 - Отмена заказа
@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Отменить заказ"""
    # FIXME OWASP:A01 - Нет проверки владельца
    # FIXME OWASP:A01 - Доставленный заказ можно отменить
    
    success = update_order_status(db, order_id, "cancelled")
    
    if not success:
        raise HTTPException(status_code=404)
    
    return {"message": "Cancelled"}
'''

print("✅ Orders модуль готов!")
print(f"   ✓ orders/models.py")
print(f"   ✓ orders/schemas.py")
print(f"   ✓ orders/services.py")
print(f"   ✓ orders/routes.py")
