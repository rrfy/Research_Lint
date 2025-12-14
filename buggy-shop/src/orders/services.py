from sqlalchemy.orm import Session
from src.orders.models import Order

def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def create_order(db: Session, user_id: int, total_price: float) -> Order:
    order = Order(user_id=user_id, total_price=total_price)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def get_user_orders(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()
