from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem

def create(db: Session, waiter_id: int, table_number: int, notes: str | None, items: list[dict]) -> Order:
    order = Order(
        table_number=table_number,
        waiter_id=waiter_id,
        notes=notes,
        total_amount=sum(i["unit_price"] * i["quantity"] for i in items)
    )
    db.add(order)
    db.flush()
    
    for item_data in items:
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=item_data["menu_item_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            notes=item_data.get("notes")
        )
        db.add(order_item)
        
    db.commit()
    db.refresh(order)
    return order

def get_by_waiter(db: Session, waiter_id: int) -> list[Order]:
    return db.query(Order).filter(Order.waiter_id == waiter_id).order_by(Order.created_at.desc()).all()

def get_all(db: Session) -> list[Order]:
    return db.query(Order).order_by(Order.created_at.desc()).all()

def get_by_id(db: Session, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id).first()

def update_status(db: Session, order: Order, new_status: str) -> Order:
    order.status = new_status
    db.commit()
    db.refresh(order)
    return order
