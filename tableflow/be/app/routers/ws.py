from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services import notification_service
from app.services.auth_service import decode_token

router = APIRouter(prefix="/ws", tags=["websockets"])

@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        token_data = decode_token(token)
        user_id = token_data.user_id
        if not user_id:
            await websocket.close(code=1008)
            return
    except Exception:
        await websocket.close(code=1008)
        return
        
    await websocket.accept()
    notification_service.register_ws(user_id, websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notification_service.unregister_ws(user_id)
