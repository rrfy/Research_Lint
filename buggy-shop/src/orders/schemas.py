from pydantic import BaseModel
from typing import Optional

class OrderBase(BaseModel):
    total_price: float
    status: str = "pending"

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True
