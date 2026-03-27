import asyncio
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.repositories import notification_repo
from app.models.notification import Notification

_connections: dict[int, WebSocket] = {}

def register_ws(user_id: int, websocket: WebSocket):
    _connections[user_id] = websocket

def unregister_ws(user_id: int):
    if user_id in _connections:
        del _connections[user_id]

async def push(user_id: int, payload_dict: dict):
    if user_id in _connections:
        ws = _connections[user_id]
        try:
            await ws.send_json(payload_dict)
        except Exception as e:
            print(f"Failed to send WS message to user {user_id}: {e}")
            unregister_ws(user_id)

def send(db: Session, user_id: int, title: str, message: str, ntype: str, related_order_id: int | None = None) -> Notification:
    notification = notification_repo.create(
        db, 
        user_id=user_id, 
        title=title, 
        message=message, 
        ntype=ntype, 
        related_order_id=related_order_id
    )
    
    payload = {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type,
        "related_order_id": notification.related_order_id
    }
    
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(push(user_id, payload))
    except RuntimeError:
        pass
        
    return notification

def get_user_notifications(db: Session, user_id: int) -> list[Notification]:
    return notification_repo.get_for_user(db, user_id)
