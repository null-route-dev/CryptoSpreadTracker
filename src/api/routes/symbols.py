from fastapi import APIRouter
from src.api.broadcast import get_manager

router = APIRouter()

@router.get("/symbols")
async def get_symbols():
    manager = get_manager()
    if not manager:
        return {"error": "Manager not initialized"}
    symbols = set()
    for ex_prices in manager.prices.values():
        symbols.update(ex_prices.keys())
    return {"symbols": list(symbols)}
