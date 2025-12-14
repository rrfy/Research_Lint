"""
products/models.py - ORM модели для товаров
Дефекты: OWASP:A01 (2), OWASP:A05 (2), STYLES (2), SOLID:SRP (1)
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from src.database import Base


class Product(Base):
    """Модель товара"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text)
    price = Column(Float)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Product {self.name}>"


class Review(Base):
    """Модель отзыва к товару"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)
    user_id = Column(Integer)
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
