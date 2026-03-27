from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str
    is_available: bool = True

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None

class MenuItemOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str
    is_available: bool
    
    class Config:
        from_attributes = True
