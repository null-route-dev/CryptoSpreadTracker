from fastapi import APIRouter, Query
from src.analyzers import discover_triangular_opportunities
from src.api.broadcast import get_manager

router = APIRouter()

@router.get("/triangular")
async def get_triangular(min_profit: float = Query(0.0)):
    manager = get_manager()
    if not manager:
        return {"error": "Manager not initialized"}
    all_prices = manager.get_all_prices()
    prices_by_symbol = {}
    for ex_id, ex_prices in all_prices.items():
        for sym, price in ex_prices.items():
            if price is not None:
                prices_by_symbol.setdefault(sym, {})[ex_id] = price
    opportunities = discover_triangular_opportunities(prices_by_symbol, min_profit)
    return opportunities
