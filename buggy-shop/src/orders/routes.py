from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.dependencies import get_current_user
from src.orders.schemas import OrderCreate, OrderResponse
from src.orders.services import get_order, create_order, get_user_orders

router = APIRouter()

@router.get("/", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return get_user_orders(db, current_user.id)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=OrderResponse)
def create_new_order(order: OrderCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return create_order(db, current_user.id, order.total_price)

__all__ = ["router"]
