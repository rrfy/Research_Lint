from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from src.database import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    total_price = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
