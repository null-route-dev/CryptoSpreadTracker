from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.api.broadcast import add_websocket_client, remove_websocket_client

router = APIRouter()

@router.websocket("/ws/aggregate")
async def websocket_aggregate(websocket: WebSocket):
    await websocket.accept()
    add_websocket_client(websocket, "aggregate")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        remove_websocket_client(websocket, "aggregate")
    except Exception:
        remove_websocket_client(websocket, "aggregate")
