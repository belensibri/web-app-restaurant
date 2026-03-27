from sqlalchemy.orm import Session
from app.repositories import menu_item_repo
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate
from app.models.menu_item import MenuItem

def get_menu(db: Session) -> list[MenuItem]:
    return menu_item_repo.get_available(db)

def get_full_menu(db: Session) -> list[MenuItem]:
    return menu_item_repo.get_all(db)

def add_item(db: Session, data: MenuItemCreate) -> MenuItem:
    return menu_item_repo.create(db, data.model_dump())

def update_item(db: Session, item_id: int, data: MenuItemUpdate) -> MenuItem | None:
    item = menu_item_repo.get_by_id(db, item_id)
    if not item:
        return None
    return menu_item_repo.update(db, item, data.model_dump(exclude_unset=True))

def toggle_availability(db: Session, item_id: int) -> MenuItem | None:
    item = menu_item_repo.get_by_id(db, item_id)
    if not item:
        return None
    return menu_item_repo.toggle_availability(db, item)
