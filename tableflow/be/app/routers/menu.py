from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemOut
from app.services import menu_service
from app.routers.deps import get_current_user

router = APIRouter(prefix="/menu", tags=["menu"])

@router.get("/", response_model=list[MenuItemOut])
def get_menu(db: Session = Depends(get_db)):
    return menu_service.get_menu(db)

@router.get("/all", response_model=list[MenuItemOut])
def get_full_menu(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return menu_service.get_full_menu(db)

@router.post("/", response_model=MenuItemOut, status_code=status.HTTP_201_CREATED)
def add_item(item_in: MenuItemCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return menu_service.add_item(db, item_in)

@router.patch("/{item_id}", response_model=MenuItemOut)
def update_item(item_id: int, item_in: MenuItemUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    item = menu_service.update_item(db, item_id, item_in)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/{item_id}/toggle", response_model=MenuItemOut)
@router.patch("/{item_id}/toggle", response_model=MenuItemOut)
def toggle_availability(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    item = menu_service.toggle_availability(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
