from fastapi import APIRouter
from src.analyzers import analyze_spreads
from src.api.broadcast import get_manager

router = APIRouter()

@router.get("/futures")
async def get_futures():
    manager = get_manager()
    if not manager or not manager.futures:
        return {"error": "Futures mode not enabled"}
    all_prices = manager.get_all_prices()
    prices_by_symbol = {}
    for ex_id, ex_prices in all_prices.items():
        for sym, data in ex_prices.items():
            if data is not None and isinstance(data, dict) and "price" in data:
                prices_by_symbol.setdefault(sym, {})[ex_id] = data
    analysis = analyze_spreads(prices_by_symbol)
    result = {}
    for symbol, entries in analysis.items():
        result[symbol] = [
            {
                "exchange": ex,
                "price": mid,
                "spread": spread,
                "funding_rate": funding
            }
            for ex, mid, _, _, spread, _, _, funding in entries
        ]
    return result
