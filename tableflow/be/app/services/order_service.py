from sqlalchemy.orm import Session
from app.repositories import order_repo, menu_item_repo
from app.schemas.order import OrderCreate
from app.models.order import Order
from app.services import kitchen_grpc_client
from app.services import notification_service

def place_order(db: Session, waiter_id: int, data: OrderCreate) -> Order | None:
    items_dicts = []
    for item in data.items:
        menu_item = menu_item_repo.get_by_id(db, item.menu_item_id)
        if not menu_item or not menu_item.is_available:
            return None
        items_dicts.append({
            "menu_item_id": item.menu_item_id,
            "quantity": item.quantity,
            "unit_price": menu_item.price,
            "notes": item.notes
        })
        
    order = order_repo.create(db, waiter_id, data.table_number, data.notes, items_dicts)
    
    accepted = kitchen_grpc_client.submit_order(order.id, order.table_number)
    if not accepted:
        return None
        
    notification_service.send(
        db, 
        user_id=waiter_id, 
        title="Order Received", 
        message=f"Order for table {order.table_number} received by kitchen.", 
        ntype="order_received", 
        related_order_id=order.id
    )
    return order

def get_my_orders(db: Session, waiter_id: int) -> list[Order]:
    return order_repo.get_by_waiter(db, waiter_id)

def get_all_orders(db: Session) -> list[Order]:
    return order_repo.get_all(db)

def update_order_status(db: Session, order_id: int, requesting_user_id: int, new_status: str) -> Order | None:
    order = order_repo.get_by_id(db, order_id)
    if not order:
        return None
        
    success = kitchen_grpc_client.update_order_status(order_id, new_status)
    if not success:
        return None
        
    order = order_repo.update_status(db, order, new_status)
    
    if new_status == "ready":
        notification_service.send(
            db,
            user_id=order.waiter_id,
            title="Order Ready!",
            message=f"Order for table {order.table_number} is ready for delivery.",
            ntype="order_ready",
            related_order_id=order.id
        )
        
    return order
