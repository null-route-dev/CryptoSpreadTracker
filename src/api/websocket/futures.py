from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.api.broadcast import add_websocket_client, remove_websocket_client

router = APIRouter()

@router.websocket("/ws/futures")
async def websocket_futures(websocket: WebSocket):
    await websocket.accept()
    add_websocket_client(websocket, "futures")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        remove_websocket_client(websocket, "futures")
    except Exception:
        remove_websocket_client(websocket, "futures")
