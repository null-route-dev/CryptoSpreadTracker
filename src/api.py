from fastapi import FastAPI, Query
from typing import Optional
from .analyzer import analyze_spreads
from .fetcher import PriceFetcherManager

app = FastAPI(title="CryptoSpreadTracker API", version="0.4.0")

_manager: Optional[PriceFetcherManager] = None

def set_manager(manager: PriceFetcherManager):
    global _manager
    _manager = manager

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/exchanges")
async def get_exchanges():
    if not _manager:
        return {"error": "Manager not initialized"}
    return {"exchanges": list(_manager.clients.keys())}

@app.get("/symbols")
async def get_symbols():
    if not _manager:
        return {"error": "Manager not initialized"}
    symbols = set()
    for ex_prices in _manager.prices.values():
        symbols.update(ex_prices.keys())
    return {"symbols": list(symbols)}

@app.get("/spreads")
async def get_spreads(
    min_spread: float = Query(0.0, description="Minimum absolute spread %"),
    top: Optional[int] = Query(None, description="Show only top N opportunities")
):
    if not _manager:
        return {"error": "Manager not initialized"}

    all_prices = _manager.get_all_prices()
    prices_by_symbol = {}
    for ex_id, ex_prices in all_prices.items():
        for sym, price in ex_prices.items():
            if price is not None:
                prices_by_symbol.setdefault(sym, {})[ex_id] = price

    analysis = analyze_spreads(prices_by_symbol)

    result = {}
    for symbol, entries in analysis.items():
        filtered = [e for e in entries if abs(e[2]) >= min_spread]
        if not filtered:
            continue
        filtered.sort(key=lambda x: abs(x[2]), reverse=True)
        if top and top > 0:
            filtered = filtered[:top]
        result[symbol] = [
            {"exchange": ex, "price": price, "spread": spread}
            for ex, price, spread in filtered
        ]

    return result
