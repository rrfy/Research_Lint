"""
products/routes.py - REST API маршруты для товаров
Дефекты: OWASP:A01 (3), OWASP:A03 (3), OWASP:A04 (2), STYLES (2)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.dependencies import get_current_user
from src.products.models import Product
from src.products.schemas import (
    ProductCreate, ProductUpdate, ProductResponse, ReviewCreate, ReviewResponse
)
from src.products.services import (
    get_product, search_products, filter_by_price, create_product,
    update_product, delete_product, get_all_products, add_review,
    get_product_reviews
)


router = APIRouter()


@router.get("/", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    """Получить список всех товаров"""
    products = get_all_products(db)
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    """Получить товар по ID"""
    product = get_product(db, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.get("/search")
def search(q: str = Query(...), db: Session = Depends(get_db)):
    """Поиск товаров"""
    products = search_products(db, q)
    return products


@router.get("/filter")
def filter_products(
    min_price: float = Query(0),
    max_price: float = Query(999999),
    db: Session = Depends(get_db)
):
    """Фильтровать товары по цене"""
    products = filter_by_price(db, min_price, max_price)
    return products


@router.post("/", response_model=ProductResponse)
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Создать новый товар"""
    db_product = create_product(db, product)
    
    if not db_product:
        raise HTTPException(status_code=400, detail="Failed to create product")
    
    return db_product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product_detail(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Обновить товар"""
    updated = update_product(db, product_id, product_update)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return updated


@router.delete("/{product_id}")
def delete_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Удалить товар"""
    success = delete_product(db, product_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted"}


@router.post("/{product_id}/reviews", response_model=ReviewResponse)
def add_product_review(
    product_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Добавить отзыв к товару"""
    
    if not get_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_review = add_review(
        db, 
        product_id, 
        current_user.id, 
        review.rating,
        review.comment
    )
    
    return db_review


@router.get("/{product_id}/reviews")
def get_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Получить отзывы товара"""
    reviews = get_product_reviews(db, product_id)
    return reviews


__all__ = ["router"]
