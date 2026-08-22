from fastapi import APIRouter, Query
from src.api.broadcast import get_manager
from src.analyzers.aggregate import aggregate_orderbooks

router = APIRouter()

@router.get("/aggregate")
async def get_aggregate(depth: int = Query(10)):
    manager = get_manager()
    if not manager:
        return {"error": "Manager not initialized"}
    if manager.mode != "orderbook":
        return {"error": "Orderbook mode is required for aggregation"}
    all_orderbooks = manager.get_all_orderbooks()
    if not all_orderbooks:
        return {"error": "No orderbook data"}
    aggregated = aggregate_orderbooks(all_orderbooks)
    result = {}
    for symbol, data in aggregated.items():
        result[symbol] = {
            "bids": data["bids"][:depth],
            "asks": data["asks"][:depth]
        }
    return result
