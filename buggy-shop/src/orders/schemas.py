from pydantic import BaseModel, Field, validator
from typing import List, Optional
from decimal import Decimal


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Количество должно быть положительным")


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    price_at_time: Decimal
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_items=1)
    
    @validator('items')
    def validate_unique_products(cls, items):
        product_ids = set()
        for item in items:
            if item.product_id in product_ids:
                raise ValueError(f"Duplicate product {item.product_id}")
            product_ids.add(item.product_id)
        return items


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: Decimal
    status: str
    created_at: str
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    status: Optional[str] = None