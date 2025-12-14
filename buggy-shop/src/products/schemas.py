"""
products/schemas.py - Pydantic схемы для товаров
Дефекты: OWASP:A03 (2), STYLES (2), SOLID:ISP (1)
"""
from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    stock: int
    
    class Config:
        from_attributes = True
        orm_mode = True


class ReviewBase(BaseModel):
    rating: int
    comment: str


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: int
    product_id: int
    user_id: int
    
    class Config:
        from_attributes = True
        orm_mode = True
