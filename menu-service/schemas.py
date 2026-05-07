from pydantic import BaseModel
from typing import List, Optional

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemResponse(MenuItemBase):
    id: int

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    items: List[MenuItemResponse] = []

    class Config:
        from_attributes = True
