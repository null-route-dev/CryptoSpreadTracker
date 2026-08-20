from fastapi import APIRouter, Query
from typing import Optional
from src.analyzers import analyze_spreads
from src.api.broadcast import get_manager, get_fees

router = APIRouter()

def parse_fees(fees_str: str) -> dict:
    result = {}
    if not fees_str:
        return result
    for part in fees_str.split(","):
        if ":" in part:
            ex, fee = part.split(":", 1)
            result[ex.strip()] = float(fee.strip())
    return result

@router.get("/spreads")
async def get_spreads(
    min_spread: float = Query(0.0),
    top: Optional[int] = Query(None),
    include_fees: bool = Query(False),
    fees: str = Query("")
):
    manager = get_manager()
    if not manager:
        return {"error": "Manager not initialized"}
    if fees:
        fees_dict = parse_fees(fees)
    else:
        fees_dict = get_fees()
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
            if include_fees and fees_dict:
                fee = fees_dict.get(ex, 0.0)
                entry["net_spread"] = spread - fee
            result[symbol].append(entry)
    return result
