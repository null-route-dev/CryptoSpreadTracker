from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.api.broadcast import add_websocket_client, remove_websocket_client

router = APIRouter()

@router.websocket("/ws/triangular")
async def websocket_triangular(websocket: WebSocket):
    await websocket.accept()
    add_websocket_client(websocket, "triangular")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        remove_websocket_client(websocket, "triangular")
    except Exception:
        remove_websocket_client(websocket, "triangular")
