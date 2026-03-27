from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate
from app.services import order_service
from app.routers.deps import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def place_order(order_in: OrderCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    order = order_service.place_order(db, current_user.id, order_in)
    if not order:
        raise HTTPException(status_code=422, detail="Invalid order data or kitchen rejected")
    return order

@router.get("/mine", response_model=list[OrderOut])
def get_my_orders(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return order_service.get_my_orders(db, current_user.id)

@router.get("/", response_model=list[OrderOut])
def get_all_orders(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return order_service.get_all_orders(db)

@router.post("/{order_id}/status", response_model=OrderOut)
@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(order_id: int, status_update: OrderStatusUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    order = order_service.update_order_status(db, order_id, current_user.id, status_update.status)
    if not order:
        raise HTTPException(status_code=422, detail="Invalid status transition or order not found")
    return order
