from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.api.broadcast import add_websocket_client, remove_websocket_client

router = APIRouter()

@router.websocket("/ws/spreads")
async def websocket_spreads(websocket: WebSocket):
    await websocket.accept()
    add_websocket_client(websocket, "spreads")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        remove_websocket_client(websocket, "spreads")
    except Exception:
        remove_websocket_client(websocket, "spreads")
