from pydantic import BaseModel
from typing import Optional, List, Literal
from decimal import Decimal
from datetime import datetime

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1
    notes: Optional[str] = None

class OrderCreate(BaseModel):
    table_number: int
    notes: Optional[str] = None
    items: List[OrderItemCreate]

class OrderStatusUpdate(BaseModel):
    status: Literal["preparing", "ready", "delivered", "cancelled"]

class OrderItemOut(BaseModel):
    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    unit_price: Decimal
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    table_number: int
    waiter_id: int
    status: str
    notes: Optional[str] = None
    total_amount: Decimal
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True
