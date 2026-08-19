from fastapi import APIRouter
from src.api.broadcast import get_manager

router = APIRouter()

@router.get("/exchanges")
async def get_exchanges():
    manager = get_manager()
    if not manager:
        return {"error": "Manager not initialized"}
    return {"exchanges": list(manager.clients.keys())}
