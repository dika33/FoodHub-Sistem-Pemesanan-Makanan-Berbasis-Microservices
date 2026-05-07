from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import httpx
import os

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Service", description="API untuk mengelola pesanan", version="1.0.0")

MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://menu-service:8002")

async def get_menu_item(menu_item_id: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{MENU_SERVICE_URL}/menus/{menu_item_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except httpx.RequestError:
            return None

@app.post("/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # Create order first to get ID
    db_order = models.Order(user_id=order.user_id, total_amount=0.0)
    db.add(db_order)
    db.flush() # flush to get db_order.id

    total_amount = 0.0
    for item in order.items:
        # Fetch menu item price from menu-service
        menu_item_data = await get_menu_item(item.menu_item_id)
        if not menu_item_data:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Menu item {item.menu_item_id} not found or menu service unavailable")
        
        price = menu_item_data["price"]
        item_total = price * item.quantity
        total_amount += item_total

        db_order_item = models.OrderItem(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price=price
        )
        db.add(db_order_item)

    db_order.total_amount = total_amount
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/orders", response_model=List[schemas.OrderResponse])
def get_orders(user_id: int = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Order)
    if user_id:
        query = query.filter(models.Order.user_id == user_id)
    orders = query.offset(skip).limit(limit).all()
    return orders

@app.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    db.refresh(order)
    return order
