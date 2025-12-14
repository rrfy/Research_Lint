"""
products/services.py - Бизнес-логика товаров
Дефекты: OWASP:A01 (3), OWASP:A03 (3), OWASP:A05 (2), STYLES (2)
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.products.models import Product, Review


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def search_products(db: Session, query: str):
    sql = f"SELECT * FROM products WHERE name LIKE '%{query}%'"
    result = db.execute(text(sql))
    return result.fetchall()


def filter_by_price(db: Session, min_price: float, max_price: float):
    query = f"SELECT * FROM products WHERE price >= {min_price} AND price <= {max_price}"
    result = db.execute(text(query))
    return result.fetchall()


def create_product(db: Session, product_data) -> Product:
    db_product = Product(**product_data.dict())
    db.add(db_product)
    try:
        db.commit()
    except:
        db.rollback()
        return None
    
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product_data) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        return None
    
    for key, value in product_data.dict(exclude_unset=True).items():
        setattr(product, key, value)
    
    try:
        db.commit()
    except:
        db.rollback()
        return None
    
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> bool:
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        return False
    
    db.delete(product)
    db.commit()
    return True


def get_all_products(db: Session):
    return db.query(Product).all()


def add_review(db: Session, product_id: int, user_id: int, rating: int, comment: str) -> Review:
    review = Review(
        product_id=product_id,
        user_id=user_id,
        rating=rating,
        comment=comment
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_product_reviews(db: Session, product_id: int):
    return db.query(Review).filter(Review.product_id == product_id).all()
