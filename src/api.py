from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from typing import List, Optional
import asyncio
from .analyzer import analyze_spreads
from .fetcher import PriceFetcherManager, discover_triangular_opportunities

app = FastAPI(title="CryptoSpreadTracker API")

_manager: Optional[PriceFetcherManager] = None
_websocket_clients: List[WebSocket] = []
_arbitrage_clients: List[WebSocket] = []
_triangular_clients: List[WebSocket] = []

def set_manager(manager: PriceFetcherManager):
    global _manager
    _manager = manager
    asyncio.create_task(_broadcast_updates())
    asyncio.create_task(_broadcast_arbitrage())
    asyncio.create_task(_broadcast_triangular())

async def _broadcast_updates():
    if not _manager:
        return
    while True:
        try:
            raw_prices = await _manager.update_queue.get()
            prices_by_symbol = {}
            for ex_id, ex_prices in raw_prices.items():
                for sym, price in ex_prices.items():
                    if price is not None:
                        prices_by_symbol.setdefault(sym, {})[ex_id] = price
            analysis = analyze_spreads(prices_by_symbol)
            message = {"type": "spreads", "data": analysis}
            for ws in _websocket_clients[:]:
                try:
                    await ws.send_json(message)
                except:
                    pass
        except Exception:
            continue

async def _broadcast_arbitrage():
    if not _manager:
        return
    while True:
        try:
            raw_prices = await _manager.update_queue.get()
            prices_by_symbol = {}
            for ex_id, ex_prices in raw_prices.items():
                for sym, price in ex_prices.items():
                    if price is not None:
                        prices_by_symbol.setdefault(sym, {})[ex_id] = price
            analysis = analyze_spreads(prices_by_symbol)
            rows = []
            for symbol, entries in analysis.items():
                if len(entries) < 2:
                    continue
                min_price = min(e[1] for e in entries)
                max_price = max(e[1] for e in entries)
                min_exchange = next(e[0] for e in entries if e[1] == min_price)
                max_exchange = next(e[0] for e in entries if e[1] == max_price)
                spread_pct = ((max_price - min_price) / min_price) * 100
                rows.append({
                    "symbol": symbol,
                    "buy_exchange": min_exchange,
                    "buy_price": min_price,
                    "sell_exchange": max_exchange,
                    "sell_price": max_price,
                    "spread_pct": spread_pct
                })
            rows.sort(key=lambda x: x["spread_pct"], reverse=True)
            message = {"type": "arbitrage", "data": rows}
            for ws in _arbitrage_clients[:]:
                try:
                    await ws.send_json(message)
                except:
                    pass
        except Exception:
            continue

async def _broadcast_triangular():
    if not _manager:
        return
    while True:
        try:
            raw_prices = await _manager.update_queue.get()
            prices_by_symbol = {}
            for ex_id, ex_prices in raw_prices.items():
                for sym, price in ex_prices.items():
                    if price is not None:
                        prices_by_symbol.setdefault(sym, {})[ex_id] = price
            opportunities = discover_triangular_opportunities(prices_by_symbol, min_profit=0.0)
            message = {"type": "triangular", "data": opportunities}
            for ws in _triangular_clients[:]:
                try:
                    await ws.send_json(message)
                except:
                    pass
        except Exception:
            continue

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
    min_spread: float = Query(0.0),
    top: Optional[int] = Query(None)
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

@app.get("/triangular")
async def get_triangular(
    min_profit: float = Query(0.0)
):
    if not _manager:
        return {"error": "Manager not initialized"}
    all_prices = _manager.get_all_prices()
    prices_by_symbol = {}
    for ex_id, ex_prices in all_prices.items():
        for sym, price in ex_prices.items():
            if price is not None:
                prices_by_symbol.setdefault(sym, {})[ex_id] = price
    opportunities = discover_triangular_opportunities(prices_by_symbol, min_profit)
    return opportunities

@app.websocket("/ws/spreads")
async def websocket_spreads(websocket: WebSocket):
    await websocket.accept()
    _websocket_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _websocket_clients.remove(websocket)
    except Exception:
        if websocket in _websocket_clients:
            _websocket_clients.remove(websocket)

@app.websocket("/ws/arbitrage")
async def websocket_arbitrage(websocket: WebSocket):
    await websocket.accept()
    _arbitrage_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _arbitrage_clients.remove(websocket)
    except Exception:
        if websocket in _arbitrage_clients:
            _arbitrage_clients.remove(websocket)

@app.websocket("/ws/triangular")
async def websocket_triangular(websocket: WebSocket):
    await websocket.accept()
    _triangular_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _triangular_clients.remove(websocket)
    except Exception:
        if websocket in _triangular_clients:
            _triangular_clients.remove(websocket)
