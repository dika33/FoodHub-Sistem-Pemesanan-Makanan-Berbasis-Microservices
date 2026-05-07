from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Menu Service", description="API untuk mengelola kategori dan menu makanan", version="1.0.0")

# Category Endpoints
@app.post("/categories", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    new_category = models.Category(name=category.name, description=category.description)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@app.get("/categories", response_model=List[schemas.CategoryResponse])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories

@app.get("/categories/{category_id}", response_model=schemas.CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()

# MenuItem Endpoints
@app.post("/menus", response_model=schemas.MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    # Validate category exists
    category = db.query(models.Category).filter(models.Category.id == item.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category does not exist")
        
    new_item = models.MenuItem(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/menus", response_model=List[schemas.MenuItemResponse])
def get_menus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    menus = db.query(models.MenuItem).offset(skip).limit(limit).all()
    return menus

@app.get("/menus/{menu_id}", response_model=schemas.MenuItemResponse)
def get_menu(menu_id: int, db: Session = Depends(get_db)):
    menu = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu

@app.delete("/menus/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    menu = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(menu)
    db.commit()
