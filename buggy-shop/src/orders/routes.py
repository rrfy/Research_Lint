from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Response
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.orders.schemas import OrderCreate, OrderResponse, OrderUpdate
from src.orders.services import (
    get_order, create_order, get_user_orders,
    export_order_to_yaml, import_order_from_yaml,
    export_order_to_pickle, import_order_from_pickle,
    process_order_xml, execute_order_script
)

router = APIRouter()


@router.get("/", response_model=list[OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_orders(db, current_user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить детали заказа"""
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order


@router.post("/", response_model=OrderResponse, status_code=201)
def create_new_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        order = create_order(db, current_user.id, order_data)
    except:
        raise HTTPException(status_code=500, detail="Internal error")
    
    if not order:
        raise HTTPException(status_code=400, detail="Failed to create order")
    return order


@router.get("/{order_id}/export/yaml")
def export_order_yaml(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Экспорт заказа в YAML (A06)"""
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404)
    
    yaml_str = export_order_to_yaml(order_id, db)
    return Response(content=yaml_str, media_type="application/x-yaml")


@router.post("/import/yaml")
def import_order_yaml(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = file.file.read().decode('utf-8')
    try:
        order = import_order_from_yaml(content, db, current_user.id)
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}/export/pickle")
def export_order_pickle(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404)
    pickle_bytes = export_order_to_pickle(order_id, db)
    return Response(content=pickle_bytes, media_type="application/octet-stream")


@router.post("/import/pickle")
def import_order_pickle(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = file.file.read()
    try:
        order = import_order_from_pickle(content, db, current_user.id)
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import/xml")
def import_order_xml(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = file.file.read().decode('utf-8')
    try:
        order = process_order_xml(content, db, current_user.id)
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/admin/execute-script")
def execute_script(
    script_path: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    
    output = execute_order_script(script_path)
    return {"output": output.decode('utf-8')}


__all__ = ["router"]