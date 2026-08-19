from fastapi import APIRouter, Query
from typing import Optional
from src.analyzers import analyze_spreads
from src.api.broadcast import get_manager

router = APIRouter()

@router.get("/spreads")
async def get_spreads(min_spread: float = Query(0.0), top: Optional[int] = Query(None)):
    manager = get_manager()
    if not manager:
        return {"error": "Manager not initialized"}
    all_prices = manager.get_all_prices()
    prices_by_symbol = {}
    for ex_id, ex_prices in all_prices.items():
        for sym, price in ex_prices.items():
            if price is not None:
                prices_by_symbol.setdefault(sym, {})[ex_id] = price
    analysis = analyze_spreads(prices_by_symbol)
    result = {}
    for symbol, entries in analysis.items():
        filtered = [e for e in entries if abs(e[4]) >= min_spread]
        if not filtered:
            continue
        filtered.sort(key=lambda x: abs(x[4]), reverse=True)
        if top and top > 0:
            filtered = filtered[:top]
        result[symbol] = []
        for ex, mid, bid, ask, spread, vwap_bid, vwap_ask, funding in filtered:
            entry = {"exchange": ex, "price": mid, "spread": spread}
            if vwap_bid is not None:
                entry["vwap_bid"] = vwap_bid
            if vwap_ask is not None:
                entry["vwap_ask"] = vwap_ask
            if funding is not None:
                entry["funding_rate"] = funding
            result[symbol].append(entry)
    return result
