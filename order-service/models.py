from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False) # Refers to User from user-service
    total_amount = Column(Float, default=0.0)
    status = Column(String(50), default="pending") # pending, completed, cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, nullable=False) # Refers to MenuItem from menu-service
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False) # Price at the time of order

    order = relationship("Order", back_populates="items")
