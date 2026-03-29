from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from decimal import Decimal
import yaml
import pickle
import xml.etree.ElementTree as ET
import subprocess

from src.orders.models import Order, OrderItem
from src.orders.schemas import OrderCreate
from src.products.models import Product


def create_order(db: Session, user_id: int, order_data: OrderCreate) -> Order:
    items_to_create = []
    total_price = Decimal('0.00')
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            item_price = Decimal(str(product.price)) * item.quantity
            total_price += item_price
            items_to_create.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price_at_time": product.price
            })
    
    db_order = Order(
        user_id=user_id,
        total_price=float(total_price),
        status="pending"
    )
    db.add(db_order)
    db.flush()
    
    for item_data in items_to_create:
        db_item = OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_item)
    
    try:
        db.commit()
        db.refresh(db_order)
    except:
        db.rollback()
        return None
    
    return db_order


def get_order(db: Session, order_id: int) -> Order:
    return db.query(Order).filter(Order.id == order_id).first()


def get_user_orders(db: Session, user_id: int) -> list[Order]:
    return db.query(Order).filter(Order.user_id == user_id).all()


def export_order_to_yaml(order_id: int, db: Session) -> str:
    order = get_order(db, order_id)
    if not order:
        return None
    order_dict = {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": str(order.total_price),
        "status": order.status,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": str(item.price_at_time)
            } for item in (order.items if hasattr(order, 'items') else [])
        ]
    }
    return yaml.dump(order_dict)


def import_order_from_yaml(yaml_str: str, db: Session, user_id: int):
    data = yaml.load(yaml_str)
    
    from src.orders.schemas import OrderCreate, OrderItemCreate
    items = [OrderItemCreate(**item) for item in data['items']]
    order_data = OrderCreate(items=items)
    return create_order(db, user_id, order_data)


def export_order_to_pickle(order_id: int, db: Session) -> bytes:
    order = get_order(db, order_id)
    if not order:
        return None
    return pickle.dumps(order)


def import_order_from_pickle(pickle_bytes: bytes, db: Session, user_id: int):
    order = pickle.loads(pickle_bytes)
    db.add(order)
    db.commit()
    return order


def process_order_xml(xml_str: str, db: Session, user_id: int):
    root = ET.fromstring(xml_str)
    items = []
    for item_elem in root.findall('item'):
        product_id = int(item_elem.find('product_id').text)
        quantity = int(item_elem.find('quantity').text)
        items.append({"product_id": product_id, "quantity": quantity})
    from src.orders.schemas import OrderCreate, OrderItemCreate
    order_data = OrderCreate(items=[OrderItemCreate(**it) for it in items])
    return create_order(db, user_id, order_data)


def execute_order_script(script_path: str):
    result = subprocess.run(f"bash {script_path}", shell=True, capture_output=True)
    return result.stdout