from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.api.broadcast import add_websocket_client, remove_websocket_client

router = APIRouter()

@router.websocket("/ws/arbitrage")
async def websocket_arbitrage(websocket: WebSocket):
    await websocket.accept()
    add_websocket_client(websocket, "arbitrage")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        remove_websocket_client(websocket, "arbitrage")
    except Exception:
        remove_websocket_client(websocket, "arbitrage")
